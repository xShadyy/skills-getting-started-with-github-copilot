document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and activity select options
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "<option value=''>-- Select an activity --</option>";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - (details.participants ? details.participants.length : 0);

        // Build participants list
        const participants = details.participants || [];
        const participantsHtml = participants.length > 0
          ? `<ul class="participants-list">${participants.map(p => `<li class="participant-item"><span class="participant-email">${p}</span><button class="unregister-btn" data-activity="${encodeURIComponent(name)}" data-email="${encodeURIComponent(p)}" title="Unregister">×</button></li>`).join('')}</ul>`
          : `<p class="no-participants">No participants yet</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            ${participantsHtml}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Attach unregister handlers
      document.querySelectorAll('.unregister-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const activity = decodeURIComponent(btn.dataset.activity);
          const email = decodeURIComponent(btn.dataset.email);

          if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) return;

          try {
            const resp = await fetch(`/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`, { method: 'DELETE' });
            const body = await resp.json();
            if (resp.ok) {
              // Refresh activities to reflect change
              await fetchActivities();
            } else {
              alert(body.detail || 'Failed to unregister');
            }
          } catch (err) {
            console.error('Error unregistering:', err);
            alert('Failed to unregister. See console for details.');
          }
        });
      });

    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities so the new participant shows up without a page reload
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
