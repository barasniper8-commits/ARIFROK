export default async function handler(req, res) {
  // Izinkan akses dari browser / WebView
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const owner = process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO;
  const token = process.env.GITHUB_TOKEN;

  if (!owner || !repo) {
    return res.status(500).json({ error: 'GITHUB_OWNER atau GITHUB_REPO belum diatur' });
  }

  try {
    const headers = {
      'Accept': 'application/vnd.github+json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };

    const ghRes = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/runs?per_page=5`,
      { headers, cache: 'no-store' }
    );

    if (!ghRes.ok) {
      const errText = await ghRes.text();
      return res.status(ghRes.status).json({ error: errText });
    }

    const data = await ghRes.json();
    const activeStatuses = ['queued', 'in_progress', 'waiting', 'requested', 'pending'];
    const runs = Array.isArray(data.workflow_runs) ? data.workflow_runs : [];
    const active = runs.some((r) => activeStatuses.includes(r.status));

    return res.status(200).json({ active });
  } catch (err) {
    return res.status(500).json({ error: 'Gagal menghubungi GitHub API' });
  }
}
