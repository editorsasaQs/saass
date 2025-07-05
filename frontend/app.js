document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const statusDiv = document.getElementById("status");

  statusDiv.innerHTML = "Uploading files...";

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Upload failed");
    }

    const jobId = data.job_id;
    statusDiv.innerHTML = `Job ID: ${jobId}<br/>Processing...`;
    pollStatus(jobId);
  } catch (err) {
    statusDiv.innerHTML = `<span class="text-red-600">${err.message}</span>`;
  }
});

async function pollStatus(jobId) {
  const statusDiv = document.getElementById("status");
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`/status/${jobId}`);
      const data = await res.json();

      if (data.status === "completed") {
        clearInterval(interval);
        statusDiv.innerHTML = `✅ Finished! <a href="/download/${jobId}" class="text-blue-600 underline">Download Video</a>`;
      } else if (data.status === "error") {
        clearInterval(interval);
        statusDiv.innerHTML = `<span class="text-red-600">Error: ${data.message}</span>`;
      } else {
        statusDiv.innerHTML = `Status: ${data.status} ${data.step ? `- ${data.step}` : ""}`;
      }
    } catch (err) {
      clearInterval(interval);
      statusDiv.innerHTML = `<span class="text-red-600">${err.message}</span>`;
    }
  }, 4000);
}