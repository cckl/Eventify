// have the divs already created in my html file / template, but just hide them
// TODO: how to dynamically create divs?

// loading animations
function loadingAnimationFade() {
  $('#loading').animate({opacity: '0.2'}, 800);
  $('#loading').animate({opacity: '1'}, 800, loadingAnimationFade);
}

function loadingAnimationSlide() {
  $('#loading2').animate({'margin-right': '-=50px'}, 400);
  $('#loading2').animate({'margin-left': '-=50px'}, 400, loadingAnimationSlide);
}

$(document).bind('ajaxSend', function() {
  $('#loading').fadeIn(400).show();
  $('#loading2').fadeIn(800).show();
  loadingAnimationFade();
  loadingAnimationSlide();
});

$(document).bind('ajaxComplete', function() {
  $('#loading').hide();
  $('#loading2').hide();
});


// event search with user artists
$('#event-search').on('submit', (evt) => {
  evt.preventDefault();

  const formInputs = {
    'city': $('#city').val(),
    'distance': $('#distance').val()
  };

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
          text: 'RSVP on Eventbrite',
          href: result['url'],
          target: '_blank'
        }).appendTo('#event-results')
        $('#event-results').append('<br><br>')
      }
    } else {
      $('#none-found').show()
    }
  });
  $('#search-area').hide();
});


// event search with recommended events
$('#recommended-events').on('submit', (evt) => {
  evt.preventDefault();
  $('#none-found').hide();

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
          text: 'RSVP on Eventbrite',
          href: result['url'],
          target: '_blank'
        }).appendTo('#recommended')
        $('#recommended').append('<br><br>')
      }
    } else {
      $('#none-found').show()
    }
  });
  $('#search-area2').hide();
});
