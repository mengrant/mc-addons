// 最小 MCP SSE 客户端：node mcpclient.mjs <mode> [...]
// mode = raw:<method>  -> 打印 result JSON
// mode = tool:<name> <paramsJson>
const BASE = 'http://localhost:19131';
const res = await fetch(BASE + '/sse', { headers: { Accept: 'text/event-stream' } });
const reader = res.body.getReader();
const dec = new TextDecoder();
let buf = '', endpoint = null;
const pending = new Map();
let idc = 1;
(async () => {
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf('\n\n')) >= 0) {
      const chunk = buf.slice(0, idx); buf = buf.slice(idx + 2);
      let ev = 'message', data = '';
      for (const line of chunk.split('\n')) {
        if (line.startsWith('event:')) ev = line.slice(6).trim();
        else if (line.startsWith('data:')) data += line.slice(5).trim();
      }
      if (ev === 'endpoint') endpoint = data;
      else if (ev === 'message' && data) {
        try { const m = JSON.parse(data);
          if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
        } catch {}
      }
    }
  }
})();
for (let i = 0; i < 80 && !endpoint; i++) await new Promise(r => setTimeout(r, 100));
const url = () => (endpoint.startsWith('http') ? endpoint : BASE + endpoint);
async function post(body) {
  const r = await fetch(url(), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (r.status >= 300) throw new Error('POST ' + r.status + ' ' + await r.text());
}
async function rpc(method, params, timeout = 120000) {
  const id = idc++;
  const p = new Promise(r => pending.set(id, r));
  await post({ jsonrpc: '2.0', id, method, params });
  return Promise.race([p, new Promise(r2 => setTimeout(() => r2({ timeout: true }), timeout))]);
}
await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'wb-client', version: '1.0' } });
await post({ jsonrpc: '2.0', method: 'notifications/initialized' });

const [mode, a, b] = process.argv.slice(2);
let out;
if (mode === 'schema') {
  const tl = await rpc('tools/list', {});
  const t = tl.result.tools.find(x => x.name === a);
  out = t || { error: 'not found' };
} else if (mode === 'tools') {
  const tl = await rpc('tools/list', {});
  out = tl.result.tools.map(t => ({ name: t.name, schema: t.inputSchema }));
} else if (mode === 'tool') {
  const params = b ? JSON.parse(b) : {};
  out = await rpc('tools/call', { name: a, arguments: params });
} else if (mode === 'raw') {
  out = await rpc(a, b ? JSON.parse(b) : {});
}
console.log(JSON.stringify(out, null, 2));
process.exit(0);
