// have the divs already created in my html file / template, but just hide them
// TODO: how to dynamically create divs?

$('#event-search').on('submit', (evt) => {
  evt.preventDefault();

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

  $('#loading').show().delay(800).slideUp(300).slideDown(400);
  $('#loading2').fadeIn(400).show();


  $.post('/event-search', formInputs, (results) => {
    console.log(results);
    if (results) {
      $('#event-results').append('<h2>Events near you</h2>')
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
        $('#event-results').append('<br><br>')
      }
    } else {
      $('#none-found').show()
    }
  });
});

$('#recommended-events').on('submit', (evt) => {
  evt.preventDefault();

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

  $.post('/recommended', formInputs, (results) => {
    console.log(results)
    if (results) {
      $('#recommended').append('<h2>Events near you</h2>')
      for (let result of results) {
        console.log(result)
        $('<img>', {
          id: 'event-img',
          src: result['img'],
          style: 'max-width: 500px'
        }).appendTo('#recommended')
        $('<div/>', {
          id: 'event-name',
          html: result['name']
        }).appendTo('#recommended')
        $('<div/>', {
          id: 'event-description',
          html: result['description']
        }).appendTo('#recommended')
        $('<div/>', {
          id: 'event-date',
          html: `${result['starts_at']} -- ${result['ends_at']}`
        }).appendTo('#recommended')
        $('<div/>', {
          id: 'event-venue',
          html: `${result['venue']},\n${result['address']}`
        }).appendTo('#recommended')
        $('<a/>', {
          id: 'event-rsvp',
          text: "RSVP on Eventbrite",
          href: result['url']
        }).appendTo('#recommended')
        $('#recommended').append('<br><br>')
      }
    } else {
      $('#none-found').show()
    }
  })
})
