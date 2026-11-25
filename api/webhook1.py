export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed. Gunakan POST.'
    });
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO;
  const workflowId = process.env.GITHUB_WORKFLOW;

  if (!token || !owner || !repo || !workflowId) {
    return res.status(500).json({
      success: false,
      error: 'Environment Variables di Vercel belum lengkap (cek GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_WORKFLOW).'
    });
  }

  const { ref = 'main', inputs = {} } = req.body || {};

  try {
    const ghRes = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowId}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ref,
          inputs
        })
      }
    );

    if (ghRes.status === 204) {
      return res.status(200).json({
        success: true,
        message: `Workflow (${workflowId}) di branch "${ref}" berhasil dijalankan!`
      });
    }

    const errData = await ghRes.json().catch(() => ({}));
    return res.status(ghRes.status).json({
      success: false,
      error: errData.message || `Gagal memicu workflow (HTTP ${ghRes.status})`
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: `Gagal menghubungi GitHub API: ${err.message}`
    });
  }
}
