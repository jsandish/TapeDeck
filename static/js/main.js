/**
 * TapeDeck - Main JavaScript
 * Provides dynamic functionality for the music rating app
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-disappear
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Handle star rating input
    setupStarRating();
    
    // Song card actions
    setupSongCardActions();
    
    // Handle add to playlist modal
    setupAddToPlaylistModal();

    // Handle mood input
    setupMoodInput();

    // Setup search functionality
    setupSearch();

    // Handle sorting functionality
    setupSorting();

    // Handle playlist management
    setupPlaylistManagement();
});

/**
 * Sets up the star rating input functionality
 */
function setupStarRating() {
    // Star rating input in form
    const starContainer = document.querySelector('.star-rating-input');
    if (starContainer) {
        const ratingInput = document.getElementById('rating');
        const stars = starContainer.querySelectorAll('.star-rating-input i');
        
        // Set initial stars based on value
        if (ratingInput.value) {
            updateStars(stars, parseFloat(ratingInput.value));
        }
        
        stars.forEach((star, index) => {
            // Show hover effect
            star.addEventListener('mouseover', function() {
                updateStars(stars, index + 1);
            });
            
            // Handle click
            star.addEventListener('click', function() {
                ratingInput.value = index + 1;
                updateStars(stars, index + 1);
            });
        });
        
        // Reset to actual value when not hovering
        starContainer.addEventListener('mouseout', function() {
            updateStars(stars, parseFloat(ratingInput.value) || 0);
        });
    }
}

/**
 * Updates star display based on rating value
 */
function updateStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove('far');
            star.classList.add('fas');
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
        }
    });
}

/**
 * Sets up song card actions
 */
function setupSongCardActions() {
    // Handle song card clicks
    const songCards = document.querySelectorAll('.song-card');
    songCards.forEach(card => {
        const songLink = card.querySelector('.song-title-link');
        if (songLink) {
            card.addEventListener('click', function(e) {
                // Don't trigger if clicking on a button or link inside the card
                if (!e.target.closest('button') && !e.target.closest('a') && 
                    !e.target.closest('.dropdown-toggle')) {
                    songLink.click();
                }
            });
        }
    });
}

/**
 * Sets up the add to playlist modal
 */
function setupAddToPlaylistModal() {
    // Set song ID in the modal form
    const addToPlaylistModal = document.getElementById('addToPlaylistModal');
    if (addToPlaylistModal) {
        addToPlaylistModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const songId = button.getAttribute('data-song-id');
            const songTitle = button.getAttribute('data-song-title');
            const songIdInput = document.getElementById('song_id');
            const modalTitle = addToPlaylistModal.querySelector('.modal-title');
            
            if (songIdInput) {
                songIdInput.value = songId;
            }
            
            if (modalTitle && songTitle) {
                modalTitle.textContent = `Add "${songTitle}" to Playlist`;
            }
        });
    }
}

/**
 * Sets up mood input functionality
 */
function setupMoodInput() {
    // Create new mood functionality
    const newMoodLink = document.getElementById('new-mood-link');
    const moodIdSelect = document.getElementById('mood_id');
    const newMoodInput = document.getElementById('new_mood_input');
    const newMoodContainer = document.getElementById('new-mood-container');
    
    if (newMoodLink && moodIdSelect && newMoodContainer) {
        newMoodLink.addEventListener('click', function(e) {
            e.preventDefault();
            newMoodContainer.classList.toggle('d-none');
            if (!newMoodContainer.classList.contains('d-none')) {
                newMoodInput.focus();
            }
        });
    }
    
    // Submit new mood via ajax
    const newMoodForm = document.getElementById('new-mood-form');
    if (newMoodForm) {
        newMoodForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(newMoodForm);
            
            fetch(newMoodForm.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add new option to select
                    const option = document.createElement('option');
                    option.value = data.mood_id;
                    option.textContent = data.mood_name;
                    option.selected = true;
                    moodIdSelect.appendChild(option);
                    
                    // Reset and hide form
                    newMoodForm.reset();
                    newMoodContainer.classList.add('d-none');
                    
                    // Show success message
                    showToast('Mood added successfully!', 'success');
                } else {
                    showToast(data.error || 'Failed to add mood', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred', 'danger');
            });
        });
    }
}

/**
 * Sets up search functionality
 */
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = searchInput.value.toLowerCase();
            const items = document.querySelectorAll('.searchable-item');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Show no results message
            const noResults = document.getElementById('no-search-results');
            if (noResults) {
                const visibleItems = document.querySelectorAll('.searchable-item:not([style*="display: none"])');
                noResults.style.display = visibleItems.length === 0 ? 'block' : 'none';
            }
        }, 300));
    }
}

/**
 * Sets up sorting functionality
 */
function setupSorting() {
    const sortLinks = document.querySelectorAll('.sort-link');
    sortLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sortBy = this.getAttribute('data-sort');
            const container = this.closest('.sortable-container');
            const items = Array.from(container.querySelectorAll('.sortable-item'));
            
            // Toggle sort direction
            const currentDirection = this.getAttribute('data-direction') || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Update all sort links
            sortLinks.forEach(sortLink => {
                sortLink.setAttribute('data-direction', sortLink === this ? newDirection : 'asc');
                sortLink.querySelector('i').className = 'fas fa-sort';
            });
            
            // Update this link's icon
            this.querySelector('i').className = `fas fa-sort-${newDirection === 'asc' ? 'up' : 'down'}`;
            
            // Sort items
            items.sort((a, b) => {
                const aValue = a.getAttribute(`data-${sortBy}`).toLowerCase();
                const bValue = b.getAttribute(`data-${sortBy}`).toLowerCase();
                
                if (newDirection === 'asc') {
                    return aValue.localeCompare(bValue);
                } else {
                    return bValue.localeCompare(aValue);
                }
            });
            
            // Reorder items
            items.forEach(item => {
                container.appendChild(item);
            });
        });
    });
}

/**
 * Sets up playlist management functions
 */
function setupPlaylistManagement() {
    // Handle removing collaborators
    const removeCollaboratorButtons = document.querySelectorAll('.remove-collaborator');
    removeCollaboratorButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to remove this collaborator?')) {
                const form = this.closest('form');
                form.submit();
            }
        });
    });
    
    // Handle removing songs from playlist
    const removeSongButtons = document.querySelectorAll('.remove-song');
    removeSongButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Remove this song from the playlist?')) {
                const form = this.closest('form');
                form.submit();
            }
        });
    });
}

/**
 * Debounce function to limit how often a function is called
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Shows a toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Toast content
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        delay: 3000
    });
    toast.show();
    
    // Remove after hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Handles the confirmation dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}