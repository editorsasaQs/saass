document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const statusDiv = document.getElementById("status");
  const progressContainer = document.getElementById("progressContainer");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");

  statusDiv.innerHTML = "";
  progressContainer.classList.remove("hidden");
  setProgress(10, "Uploading files...");

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
    setProgress(15, "Queued for processing...");
    pollStatus(jobId);
  } catch (err) {
    progressContainer.classList.add("hidden");
    statusDiv.innerHTML = `<span class="text-red-300">${err.message}</span>`;
  }
});

async function pollStatus(jobId) {
  const statusDiv = document.getElementById("status");
  const progressContainer = document.getElementById("progressContainer");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`/status/${jobId}`);
      const data = await res.json();

      if (data.status === "completed") {
        clearInterval(interval);
        setProgress(100, "Completed ✔️");
        statusDiv.innerHTML = `<a href="/download/${jobId}" class="text-yellow-300 underline font-medium">Download Edited Video</a>`;
      } else if (data.status === "error") {
        clearInterval(interval);
        progressContainer.classList.add("hidden");
        statusDiv.innerHTML = `<span class="text-red-300">Error: ${data.message}</span>`;
      } else {
        const stepProgress = {
          transcription: 30,
          scene_planning: 50,
          video_editing: 80,
        };
        const pct = stepProgress[data.step] || 20;
        setProgress(pct, `Processing: ${data.step || data.status}`);
      }
    } catch (err) {
      clearInterval(interval);
      progressContainer.classList.add("hidden");
      statusDiv.innerHTML = `<span class="text-red-300">${err.message}</span>`;
    }
  }, 4000);
}

function setProgress(percent, text) {
  progressBar.style.width = `${percent}%`;
  progressText.textContent = text;
}