// Apply font size dynamically
function updateFontSize(size) {
    const body = document.body;
    if (size === 'small') {
      body.style.fontSize = '14px'; // Small font size
    } else if (size === 'standard') {
      body.style.fontSize = '16px'; // Standard font size
    } else if (size === 'large') {
      body.style.fontSize = '20px'; // Large font size
    }
  }
  
  // Apply contrast dynamically
  function updateContrast(contrast) {
    const body = document.body;
    if (contrast === 'weak') {
      body.style.backgroundColor = '#f4f4f4'; // Light background
      body.style.color = '#666'; // Weaker text color
    } else if (contrast === 'standard') {
      body.style.backgroundColor = '#fff'; // Standard white background
      body.style.color = '#333'; // Standard dark text
    } else if (contrast === 'strong') {
      body.style.backgroundColor = '#000'; // Black background
      body.style.color = '#fff'; // White text
    }
  }
  
  // Restore settings globally on every page load
  function restoreAccessibilitySettings() {
    // Restore and apply font size
    const savedFontSize = localStorage.getItem('fontSize') || 'standard'; // Default to 'standard'
    updateFontSize(savedFontSize);
  
    // Restore and apply contrast
    const savedContrast = localStorage.getItem('contrast') || 'standard'; // Default to 'standard'
    updateContrast(savedContrast);
  
    // Restore screen reader toggle (optional, currently non-functional)
    const savedScreenReader = localStorage.getItem('screenReader') || 'off';
    if (savedScreenReader === 'on') {
      console.log("Screen reader enabled (but currently non-functional).");
    }
  }
  
  // Automatically restore settings on page load
  window.onload = restoreAccessibilitySettings;
  