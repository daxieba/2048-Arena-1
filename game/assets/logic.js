/* =========================================================
 * 2048 核心逻辑（纯函数，无 DOM 依赖）
 * 同时被浏览器端（<script src>）和 Node 单元测试加载
 * ========================================================= */

/* 根据方向返回"行序扫描 + 行内移动方向"配置 */
function dirConfig(dir) {
  switch (dir) {
    case 'left':  return { rowMajor: true,  reverse: false };
    case 'right': return { rowMajor: true,  reverse: true  };
    case 'up':    return { rowMajor: false, reverse: false };
    case 'down':  return { rowMajor: false, reverse: true  };
    default: throw new Error('unknown direction: ' + dir);
  }
}

/**
 * 对网格做一次移动。
 * @param {number[][]} grid 二维数组（不允许原地修改）
 * @param {string} dir 'left'|'right'|'up'|'down'
 * @returns {{grid:number[][], score:number, moved:boolean}}
 *   moved 表示该方向是否产生了任何位移或合并
 */
function move(grid, dir) {
  const size = grid.length;
  const { rowMajor, reverse } = dirConfig(dir);

  // 深拷贝网格
  const g = grid.map(row => row.slice());
  let score = 0;
  let moved = false;

  const line = (k) => rowMajor ? g[k] : g.map(r => r[k]);

  for (let k = 0; k < size; k++) {
    const cells = line(k);                       // 当前行/列
    const vals = cells.slice().filter(v => v !== 0);
    if (reverse) vals.reverse();

    // 从前往后合并相邻相等的格子（合并后不参与后续合并）
    const out = [];
    for (let i = 0; i < vals.length; i++) {
      if (i + 1 < vals.length && vals[i] === vals[i + 1]) {
        out.push(vals[i] * 2);
        score += vals[i] * 2;
        i++;                                     // 跳过已合并的格子
      } else {
        out.push(vals[i]);
      }
    }
    while (out.length < size) out.push(0);
    if (reverse) out.reverse();

    // 写入并检测是否有变化
    for (let i = 0; i < size; i++) {
      const target = rowMajor ? g[k][i] : g[i][k];
      if (target !== out[i]) {
        moved = true;
        if (rowMajor) g[k][i] = out[i]; else g[i][k] = out[i];
      }
    }
  }

  return { grid: g, score, moved };
}

/** 返回所有空格子坐标 [{r, c}, ...] */
function emptyCells(grid) {
  const out = [];
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      if (grid[r][c] === 0) out.push({ r, c });
    }
  }
  return out;
}

/** 随机选一个空格子生成新块：90% 生成 2，10% 生成 4（返回新网格） */
function spawnRandom(grid) {
  const cells = emptyCells(grid);
  if (cells.length === 0) return grid;
  const pick = cells[Math.floor(Math.random() * cells.length)];
  const value = Math.random() < 0.9 ? 2 : 4;
  const g = grid.map(row => row.slice());
  g[pick.r][pick.c] = value;
  return g;
}

/** 是否还有任何可移动方向 */
function canMove(grid) {
  if (emptyCells(grid).length > 0) return true;
  const size = grid.length;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      const v = grid[r][c];
      if (c + 1 < size && grid[r][c + 1] === v) return true;
      if (r + 1 < size && grid[r + 1][c] === v) return true;
    }
  }
  return false;
}

/** 网格中是否已达成目标（出现 >= target 的块） */
function hasWon(grid, target) {
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      if (grid[r][c] >= target) return true;
    }
  }
  return false;
}

/** 初始化新局：全是 0 的 size×size 网格，然后生成两个初始块 */
function newGrid(size) {
  let g = Array.from({ length: size }, () => Array(size).fill(0));
  g = spawnRandom(g);
  g = spawnRandom(g);
  return g;
}

/* =========================================================
 * 2048 AI：Expectimax 搜索 + 启发式评分
 * 供"自动玩"功能使用；纯函数，无随机，可在 Node 中测试
 * ========================================================= */

/* 按棋盘尺寸决定 Expectimax 搜索深度（大棋盘分支多，深度相应调浅）。
   两档强度：normal 普通 / master 大师（每档深度 +1）。
   实测 master 最慢约 13ms（4×4 depth5），对 1.5 秒/步的自动玩毫无压力。 */
const AI_DEPTH = {
  normal: { 3: 5, 4: 4, 5: 3, 6: 2, 7: 1, 8: 1 },
  master: { 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 2 },
};
const SPAWN_2 = 0.9;  // 与 spawnRandom 保持一致：90% 生成 2

/**
 * 启发式评分：奖励空格多、行/列单调、最大块贴角落；
 * 惩罚相邻方块差值大（平滑度差）。
 */
function aiScore(grid) {
  const size = grid.length;
  let empty = 0;
  let smooth = 0;

  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      const v = grid[r][c];
      if (v === 0) { empty++; continue; }
      if (c + 1 < size && grid[r][c + 1] !== 0) smooth -= Math.abs(v - grid[r][c + 1]);
      if (r + 1 < size && grid[r + 1][c] !== 0) smooth -= Math.abs(v - grid[r + 1][c]);
    }
  }

  // 单调性：每行/每列分别累计"递增惩罚"与"递减惩罚"，取较小者（鼓励单向递增或递减）
  let mono = 0;
  const lineMono = (arr) => {
    let inc = 0, dec = 0;
    for (let i = 1; i < arr.length; i++) {
      const a = arr[i - 1], b = arr[i];
      if (a === 0 || b === 0) continue;
      if (a > b) inc += Math.log2(a) - Math.log2(b);
      if (a < b) dec += Math.log2(b) - Math.log2(a);
    }
    return Math.min(inc, dec);
  };
  for (let r = 0; r < size; r++) mono += lineMono(grid[r]);
  for (let c = 0; c < size; c++) mono += lineMono(grid.map(row => row[c]));

  // 最大块奖励：用原值 × 权重（大块数值将主导评分，AI 会优先保护并持续合成它），
  // 位于角落时额外加成
  let maxV = 0, maxR = 0, maxC = 0;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (grid[r][c] > maxV) { maxV = grid[r][c]; maxR = r; maxC = c; }
    }
  }
  const inCorner = (maxR === 0 || maxR === size - 1) && (maxC === 0 || maxC === size - 1);
  const maxBonus = maxV * 1.0;
  const cornerBonus = inCorner ? maxV * 1.0 : 0;

  return -smooth * 0.1 - mono * 1.0 + empty * 2.7 + maxBonus + cornerBonus;
}

/**
 * Expectimax 搜索。
 * 玩家层取最优；随机层按"空格均匀 + 0.9/0.1 生成 2/4"求期望值。
 */
function expectimax(grid, depth, playerTurn) {
  if (depth <= 0) return aiScore(grid);

  if (playerTurn) {
    let best = -Infinity;
    const dirs = ['left', 'right', 'up', 'down'];
    for (const d of dirs) {
      const res = move(grid, d);
      if (res.moved) {
        const v = expectimax(res.grid, depth - 1, false);
        if (v > best) best = v;
      }
    }
    return best === -Infinity ? aiScore(grid) : best;
  }

  // 随机层（对手是"随机生成新块"）：求期望值
  const cells = emptyCells(grid);
  if (cells.length === 0) return aiScore(grid);
  let exp = 0;
  for (const { r, c } of cells) {
    const g2 = grid.map(row => row.slice()); g2[r][c] = 2;
    const g4 = grid.map(row => row.slice()); g4[r][c] = 4;
    exp += SPAWN_2 * expectimax(g2, depth - 1, true)
         + (1 - SPAWN_2) * expectimax(g4, depth - 1, true);
  }
  return exp / cells.length;
}

/** 返回 AI 认为最优的移动方向；所有方向都无法移动时返回 null。
 *  @param {string} [level] 'normal' 普通档 / 'master' 大师档，默认 normal */
function aiBestMove(grid, level) {
  const table = AI_DEPTH[level] || AI_DEPTH.normal;
  const depth = table[grid.length] !== undefined ? table[grid.length] : 2;
  const dirs = ['left', 'right', 'up', 'down'];
  let bestDir = null;
  let bestVal = -Infinity;
  for (const d of dirs) {
    const res = move(grid, d);
    if (!res.moved) continue;
    const v = expectimax(res.grid, depth - 1, false);
    if (v > bestVal) { bestVal = v; bestDir = d; }
  }
  return bestDir;
}

/* Node（CommonJS）导出 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    move, emptyCells, spawnRandom, canMove, hasWon, newGrid, dirConfig,
    aiScore, expectimax, aiBestMove, AI_DEPTH,
  };
}
