(function ($) {
  "use strict";

  $(function () {
    var header = $(".start-style");

    // Debounce function to limit scroll events
    function debounce(func, wait = 20, immediate = true) {
      var timeout;
      return function () {
        var context = this, args = arguments;
        var later = function () {
          timeout = null;
          if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
      };
    }

    // Scroll event with debounce
    $(window).scroll(debounce(function () {
      var scroll = $(window).scrollTop();
      if (scroll >= 10) {
        header.removeClass('start-style').addClass("scroll-on");
      } else {
        header.removeClass("scroll-on").addClass('start-style');
      }
    }));

    // Animation removal on document load
    $(document).ready(function () {
      $('body.hero-anime').removeClass('hero-anime');
    });

    // Menu hover effect for desktop screens
    $('body').on('mouseenter mouseleave', '.nav-item', function (e) {
      if ($(window).width() > 750) {
        var _d = $(e.target).closest('.nav-item');
        _d.addClass('show');
        setTimeout(function () {
          _d[_d.is(':hover') ? 'addClass' : 'removeClass']('show');
        }, 1);
      }
    });

    // External links open in a new tab
    $(document.links).filter(function () {
      return this.hostname != window.location.hostname;
    }).attr('target', '_blank');
  });
})(jQuery);
