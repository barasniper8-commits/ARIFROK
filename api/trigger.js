const https = require('https');

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO;
  const workflowId = process.env.GITHUB_WORKFLOW;

  if (!token || !owner || !repo || !workflowId) {
    return res.status(500).json({
      error: 'Konfigurasi Environment Variables di Vercel belum lengkap.'
    });
  }

  let bodyData = req.body;
  if (typeof bodyData === 'string') {
    try {
      bodyData = JSON.parse(bodyData);
    } catch (e) {
      bodyData = {};
    }
  }
  bodyData = bodyData || {};

  const ref = bodyData.ref || 'main';
  const inputs = bodyData.inputs || {};
  const payload = JSON.stringify({ ref, inputs });

  const options = {
    hostname: 'api.github.com',
    path: `/repos/${owner}/${repo}/actions/workflows/${workflowId}/dispatches`,
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload),
      'User-Agent': 'Vercel-Workflow-Power-Switch'
    }
  };

  const ghReq = https.request(options, (ghRes) => {
    let raw = '';
    ghRes.on('data', (chunk) => {
      raw += chunk;
    });
    ghRes.on('end', () => {
      if (ghRes.statusCode === 204) {
        return res.status(200).json({
          success: true,
          message: `Workflow (${workflowId}) di branch "${ref}" berhasil dijalankan!`
        });
      }

      let parsed = {};
      try {
        parsed = raw ? JSON.parse(raw) : {};
      } catch (e) {
        parsed = {};
      }

      return res.status(ghRes.statusCode || 500).json({
        success: false,
        error: parsed.message || `Gagal memicu workflow (HTTP ${ghRes.statusCode})`
      });
    });
  });

  ghReq.on('error', () => {
    return res.status(500).json({
      success: false,
      error: 'Terjadi kesalahan jaringan saat menghubungi GitHub API.'
    });
  });

  ghReq.write(payload);
  ghReq.end();
};
