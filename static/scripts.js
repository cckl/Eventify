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
  $('#loading').empty();
  $('#loading2').empty();
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
      $('#event-header').html('<h2>Events near you</h2><br>')
      for (let result of results) {
        $('#event-results').append(`
          <div class="event-div" id="orange-bg">
              <div class="rect-img img-fluid">
                <img class="event-img" src="${result['img']}">
              </div>
              <div class="event-text">
                <div class="row">
                  <div class="col-4">
                    <p>${result['starts_at']}</p>
                  </div>
                  <div class="col-8">
                    <h4>${result['name']}</h4>
                    <p>${result['venue']}</p>
                    <a class="btn btn-info" href="${result['url']}" target="_blank">RSVP on Eventbrite</a>
                  </div>
                </div>
              </div>
            </div>
          `)
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
      $('#event-results').append('<h2>You might like</h2>')
      for (let result of results) {
        $('#event-results').append(`
          <div class="event-div">
              <div class="rect-img img-fluid">
                <img class="event-img" src="${result['img']}">
              </div>
              <div class="event-text">
                <div class="row">
                  <div class="col-4">
                    <p>${result['starts_at']}</p>
                  </div>
                  <div class="col-8">
                    <h4>${result['name']}</h4>
                    <p>${result['venue']}</p>
                    <a class="btn btn-info" href="${result['url']}" target="_blank">RSVP on Eventbrite</a>
                  </div>
                </div>
              </div>
            </div>
          `)
      }
    } else {
      $('#none-found').show()
    }
  });
  $('#search-area2').hide();
});


$('#search-again').on('click', () => {
  $('#event-results').empty()
  $('#search-area').show()
  $('#search-area2').show()
})
