// have the divs already created in my html file / template, but just hide them
// TODO: how to dynamically create divs?

$('#event-search').on('submit', (evt) => {
  evt.preventDefault();

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

  $.post('/event-search', formInputs, (results) => {
    console.log(results);
    // if (results.length == 0) {
    //   $('#event-results').html("<p>Sorry, no events near you were found ☹️</p><p><a href='/search-events'>Try your search with a different city</a>, or search for related events!</p>");
    // } else {
      for (let result of results) {
        $('<img>', {
          id: 'event-img',
          src: result['img'],
          style: 'max-width: 500px'
        }).appendTo('#event-results')
        $('<div/>', {
          id: 'event-name',
          html: result['name']
        }).appendTo('#event-results')
        $('<div/>', {
          id: 'event-description',
          html: result['description']
        }).appendTo('#event-results')
        $('<div/>', {
          id: 'event-date',
          html: `${result['starts_at']} -- ${result['ends_at']}`
        }).appendTo('#event-results')
        $('<div/>', {
          id: 'event-venue',
          html: `${result['venue']},\n${result['address']}`
        }).appendTo('#event-results')
        $('<a/>', {
          id: 'event-rsvp',
          text: "RSVP on Eventbrite",
          href: result['url']
        }).appendTo('#event-results')

        // $('#event-img').attr("src", result['img'])
        // $('#event-name').html(result['name'])
        // $('#event-description').html(result['description'])
        // $('#event-date').html(`${result['starts_at']} -- ${result['ends_at']}`)
        // $('#event-venue').html(`${result['venue']},\n${result['address']}`)
        // $('#event-rsvp').attr("href", result['url'])
        // $('#event-rsvp').text("RSVP on Eventbrite")
      };
    });
  });
