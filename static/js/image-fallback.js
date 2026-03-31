/**
 * Image Fallback Handler
 * 
 * Provides centralized error handling for image loading failures.
 * Replaces inline onerror handlers with a clean, maintainable approach.
 * 
 * **Pattern:**
 * <img data-fallback-image src="..." alt="...">
 * <span class="img-fallback is-hidden">No image</span>
 * 
 * When image fails to load:
 * - Hide: <img> element (add 'is-hidden' class)
 * - Show: <span> fallback text (remove 'is-hidden' class)
 */

(function () {
  // ====================================================================
  // Image Fallback Handler
  // ====================================================================

  /**
   * Initializes image fallback handlers for all images with data-fallback-image
   * Attaches error listeners that toggle visibility between image and fallback text
   */
  function initImageFallbacks() {
    var images = document.querySelectorAll('[data-fallback-image]');

    if (images.length === 0) {
      console.log('ℹ️ No images with [data-fallback-image] found');
      return;
    }

    images.forEach(function (img) {
      img.addEventListener('error', function () {
        // Hide the broken image
        img.classList.add('is-hidden');

        // Show the fallback text (next sibling)
        var fallback = img.nextElementSibling;
        if (fallback && fallback.classList.contains('img-fallback')) {
          fallback.classList.remove('is-hidden');
          console.warn('⚠️ Image failed to load, showing fallback:', img.src);
        }
      });
    });

    console.log(`✅ Image fallbacks initialized for ${images.length} images`);
  }

  // ====================================================================
  // Initialize on DOMContentLoaded
  // ====================================================================

  document.addEventListener('DOMContentLoaded', function () {
    initImageFallbacks();
  });

  // ====================================================================
  // Expose for debugging
  // ====================================================================

  window.ImageFallbackDebug = {
    initImageFallbacks: initImageFallbacks,
    getImageCount: function () {
      return document.querySelectorAll('[data-fallback-image]').length;
    },
    logImages: function () {
      var images = document.querySelectorAll('[data-fallback-image]');
      console.table(Array.from(images).map(function (img) {
        return {
          src: img.src,
          alt: img.alt,
          loaded: img.complete && img.naturalHeight > 0,
        };
      }));
    },
  };
})();
