/* 2048 核心逻辑单元测试（Node 运行：node tools/test_logic.js） */
'use strict';
const assert = require('assert');
const { move, emptyCells, spawnRandom, canMove, hasWon, newGrid, dirConfig } =
  require('../game/assets/logic.js');
const { aiBestMove, aiScore, expectimax, AI_DEPTH } =
  require('../game/assets/logic.js');

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log('  ✓ ' + name); }
  catch (e) { failed++; console.error('  ✗ ' + name + '\n    ' + e.message); }
}
function eq(a, b, msg) { assert.deepStrictEqual(a, b, msg); }

/* ---------- 移动 / 合并 ---------- */
test('左移：空位对齐', () => {
  const g = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const r = move(g, 'left');
  eq(r.grid, [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]);
  assert.strictEqual(r.moved, false);
  assert.strictEqual(r.score, 0);
});

test('左移：同值合并一次且只合并一次', () => {
  const g = [[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const r = move(g, 'left');
  eq(r.grid, [[4, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]);
  assert.strictEqual(r.score, 8);
});

test('右移：反向合并正确', () => {
  const g = [[2, 2, 4, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const r = move(g, 'right');
  eq(r.grid, [[0, 0, 4, 8], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]);
  assert.strictEqual(r.score, 12);
});

test('上移：列方向合并', () => {
  const g = [[2, 0, 0, 0], [2, 0, 0, 0], [4, 0, 0, 0], [4, 0, 0, 0]];
  const r = move(g, 'up');
  eq(r.grid, [[4, 0, 0, 0], [8, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]);
  assert.strictEqual(r.score, 12);
});

test('下移：列方向反向合并', () => {
  const g = [[2, 0, 0, 0], [2, 0, 0, 0], [2, 0, 0, 0], [2, 0, 0, 0]];
  const r = move(g, 'down');
  eq(r.grid, [[0, 0, 0, 0], [0, 0, 0, 0], [4, 0, 0, 0], [4, 0, 0, 0]]);
  assert.strictEqual(r.score, 8);
});

test('中间隔空也能合并：2 0 2 2 -> 4 2', () => {
  const g = [[2, 0, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const r = move(g, 'left');
  eq(r.grid, [[4, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]);
  assert.strictEqual(r.score, 4);
});

test('没有移动时不改分数且 moved=false', () => {
  const g = [[2, 4, 8, 16], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const r = move(g, 'left');
  eq(r.grid, g);
  assert.strictEqual(r.moved, false);
  assert.strictEqual(r.score, 0);
});

test('原网格不被修改（纯函数）', () => {
  const g = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const before = JSON.stringify(g);
  move(g, 'left');
  assert.strictEqual(JSON.stringify(g), before);
});

/* ---------- 工具函数 ---------- */
test('emptyCells 统计', () => {
  const g = [[2, 0, 0, 0], [0, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 8]];
  assert.strictEqual(emptyCells(g).length, 13);
});

test('spawnRandom 只往空格生成 2 或 4', () => {
  const g = [[2, 4, 8, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096], [0, 0, 0, 0]];
  for (let i = 0; i < 200; i++) {
    const r = spawnRandom(g);
    const diffs = [];
    for (let x = 0; x < 4; x++)
      for (let y = 0; y < 4; y++)
        if (r[x][y] !== g[x][y]) diffs.push(r[x][y]);
    assert.strictEqual(diffs.length, 1);
    assert.ok(diffs[0] === 2 || diffs[0] === 4);
  }
});

test('canMove：无空格且无相邻同值 -> false', () => {
  const g = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]];
  assert.strictEqual(canMove(g), false);
});

test('canMove：有相邻同值 -> true', () => {
  const g = [[2, 2, 4, 8], [4, 8, 16, 32], [64, 128, 256, 512], [1024, 2048, 4096, 8192]];
  assert.strictEqual(canMove(g), true);
});

test('hasWon：达到目标才为 true', () => {
  const g = [[2048, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  assert.strictEqual(hasWon(g, 2048), true);
  assert.strictEqual(hasWon(g, 4096), false);
});

test('newGrid：生成 size×size 且恰有 2 个初始块', () => {
  const g = newGrid(4);
  assert.strictEqual(g.length, 4);
  assert.strictEqual(g[0].length, 4);
  assert.strictEqual(emptyCells(g).length, 14);
  const g6 = newGrid(6);
  assert.strictEqual(g6.length, 6);
  assert.strictEqual(emptyCells(g6).length, 34);
});

/* ---------- 随机移动长程不变量 ---------- */
test('随机移动 2000 步：分数非负、网格形状不变', () => {
  let g = newGrid(4);
  let score = 0;
  const dirs = ['left', 'right', 'up', 'down'];
  for (let i = 0; i < 2000; i++) {
    const dir = dirs[Math.floor(Math.random() * 4)];
    const r = move(g, dir);
    if (r.moved) {
      score += r.score;
      g = r.grid;
      g = spawnRandom(g);
      assert.ok(score >= 0);
    }
    if (!canMove(g)) { g = newGrid(4); score = 0; }
  }
  assert.strictEqual(g.length, 4);
  assert.ok(g.every(row => row.length === 4));
});

/* ---------- 3×3 棋盘同样成立 ---------- */
test('3×3 棋盘移动正确', () => {
  const g = [[2, 2, 4], [0, 0, 0], [0, 0, 0]];
  const r = move(g, 'left');
  eq(r.grid, [[4, 4, 0], [0, 0, 0], [0, 0, 0]]);
  assert.strictEqual(r.score, 4);
});

/* ---------- AI ---------- */
test('aiBestMove：存在有效方向时必返回合法方向', () => {
  const g = [[2, 2, 4, 8], [16, 32, 64, 128], [256, 512, 1024, 2048], [4096, 8192, 16384, 32768]];
  const dir = aiBestMove(g);
  assert.ok(['left', 'right', 'up', 'down'].includes(dir));
  assert.strictEqual(move(g, dir).moved, true);
});

test('aiBestMove：死局返回 null', () => {
  const g = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]];
  assert.strictEqual(aiBestMove(g), null);
});

test('aiBestMove 各尺寸都能快速决策', () => {
  for (const size of [3, 4, 5, 6, 7, 8]) {
    const g = newGrid(size);
    const t0 = Date.now();
    const dir = aiBestMove(g);
    const dt = Date.now() - t0;
    assert.ok(dt < 1000, size + 'x' + size + ' 决策耗时 ' + dt + 'ms 过长');
    if (dir) assert.strictEqual(move(g, dir).moved, true);
  }
});

test('AI 自动对弈：300 步内不崩溃且分数单调', () => {
  let g = newGrid(4);
  let score = 0;
  for (let i = 0; i < 300; i++) {
    if (!canMove(g)) break;
    const dir = aiBestMove(g);
    if (!dir) break;
    const r = move(g, dir);
    assert.strictEqual(r.moved, true);
    score += r.score;
    g = spawnRandom(r.grid);
  }
  assert.ok(score >= 0);
});

test('AI 4x4 至少能合出 256', () => {
  // 多次对局取最好成绩，验证 AI 不是乱滑（随机下限几乎不可能合出 256）
  let best = 0;
  for (let game = 0; game < 5; game++) {
    let g = newGrid(4);
    let maxTile = 0;
    for (let i = 0; i < 2000; i++) {
      if (!canMove(g)) break;
      const dir = aiBestMove(g);
      if (!dir) break;
      const r = move(g, dir);
      g = spawnRandom(r.grid);
      for (const row of g) for (const v of row) if (v > maxTile) maxTile = v;
    }
    if (maxTile > best) best = maxTile;
  }
  assert.ok(best >= 256, 'AI 最好成绩只有 ' + best + '，强度不足');
});

test('aiScore 对更优局面给更高分', () => {
  // 空格多的局面应比几乎填满的局面得分高
  const open = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
  const full = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]];
  assert.ok(aiScore(open) > aiScore(full));
});

console.log('\n结果：' + passed + ' 通过，' + failed + ' 失败');
process.exit(failed ? 1 : 0);
