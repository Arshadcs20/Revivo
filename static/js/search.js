$(document).ready(function () {
  $("#searchForm").on("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission

    var searchQuery = $("#searchInput").val().trim(); // Get the search query and trim whitespace
    if (searchQuery) {
      // Remove previous highlights and restore original content
      $(".highlight").each(function () {
        var content = $(this).html();
        $(this).replaceWith(content);
      });

      // Filter and display relevant content
      filterContent(searchQuery);
    }
  });

  function filterContent(query) {
    var contentElements = $("#content").children(); // Get all child elements within the content container
    var regex = new RegExp(query, "i"); // Create a case-insensitive regular expression

    contentElements.each(function () {
      var element = $(this);
      if (element.text().search(regex) === -1) {
        element.hide(); // Hide elements that do not match the query
      } else {
        element.show(); // Show elements that match the query
        highlightSearchTerms(element, query); // Highlight matching terms within the visible elements
      }
    });

    scrollToFirstMatch();
  }

  function highlightSearchTerms(element, query) {
    var regex = new RegExp("(" + query + ")", "gi");
    var highlightedContent = element
      .html()
      .replace(regex, '<span class="highlight">$1</span>');
    element.html(highlightedContent);
  }

  function scrollToFirstMatch() {
    var firstHighlight = $(".highlight").first();
    if (firstHighlight.length) {
      $("html, body").animate(
        {
          scrollTop: firstHighlight.offset().top - 100, // Adjust the offset as needed
        },
        1000
      );
    }
  }
});
