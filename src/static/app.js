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

      // Clear loading message
      activitiesList.innerHTML = "";

      // simple HTML-escape helper
      function escapeHtml(str = "") {
        return String(str).replace(/[&<>"']/g, (s) =>
          ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[s])
        );
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // render static parts of the card; participants will be constructed with DOM APIs
        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>

          <div class="participants-section">
            <strong>Participants</strong>
            <div class="participants-wrapper"></div>
          </div>
        `;

        // Append card first
        activitiesList.appendChild(activityCard);

        // Fill participants area using DOM to keep it safe and allow attaching handlers
        const wrapper = activityCard.querySelector('.participants-wrapper');

        if (Array.isArray(details.participants) && details.participants.length) {
          const ul = document.createElement('ul');
          ul.className = 'participants-list';

          details.participants.forEach((p) => {
            const li = document.createElement('li');
            li.className = 'participant-item';

            const span = document.createElement('span');
            span.className = 'participant-email';
            span.textContent = p;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'delete-participant';
            btn.setAttribute('aria-label', `Remove ${p} from ${name}`);
            // Use a visible cross for the icon
            btn.textContent = '✖';
            // Store needed data
            btn.dataset.activity = name;
            btn.dataset.email = p;

            // Attach handler to unregister this participant
            btn.addEventListener('click', async (ev) => {
              ev.preventDefault();
              btn.disabled = true;
              try {
                const res = await fetch(`/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(p)}`, {
                  method: 'POST',
                });

                if (res.ok) {
                  // Refresh the activities list so availability and participants update
                  fetchActivities();
                } else {
                  const body = await res.json().catch(() => ({}));
                  console.error('Failed to unregister:', body.detail || body.message || res.statusText);
                  btn.disabled = false;
                }
              } catch (error) {
                console.error('Error unregistering participant:', error);
                btn.disabled = false;
              }
            });

            li.appendChild(span);
            li.appendChild(btn);
            ul.appendChild(li);
          });

          wrapper.appendChild(ul);
        } else {
          wrapper.innerHTML = `<p class="no-participants"><em>No participants yet</em></p>`;
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
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
        // Refresh activities to show the newly registered participant and updated availability
        fetchActivities();
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
