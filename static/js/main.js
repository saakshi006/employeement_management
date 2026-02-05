// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    console.log('Skill Match System Loaded');
    
    // Add any global event listeners or initializations here
    
    // Example: Confirmation for delete buttons (if not handled by modal/page)
    const deleteLinks = document.querySelectorAll('.btn-danger');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.tagName === 'A' && this.textContent.toLowerCase().includes('delete')) {
                // If it's a link, we might want to confirm, but we have a dedicated page for delete.
                // So this is just a placeholder.
            }
        });
    });
});
