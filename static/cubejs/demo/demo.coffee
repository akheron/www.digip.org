$ ->
  $('#status').text('Initializing')

  progress = ->
    # Add a dot each second
    $('#status').text((index, text) -> "#{text}.");

  initialized = ->
    # Stop adding dots
    clearInterval(progressHandle)

    # Measure the duration of initialization
    end = new Date
    duration = (end - start) / 1000
    $('#status').text("Initialization done in #{duration} seconds.")

    # Show the scrambler
    $('#randomstate').css('visibility', 'visible')

  $('#randomstate button').on('click', ->
    # Hide the initialization duration on first scramble
    $('#status').hide()

    # Generate a scramble
    Cube.asyncScramble((alg) ->
      # Strip spaces
      stripped = alg.replace(/\s+/g, '')

      # Show the algorithm and a visualization
      url = "http://cube.crider.co.uk/visualcube.png?size=150&alg=#{stripped}"
      $('#randomstate .result').html("#{alg}<br><img src=\"#{url}\">")
    )
  )

  # Setup progress callback
  progressHandle = setInterval(progress, 1000)

  # Start measuring time
  start = new Date

  # Start initializing
  Cube.asyncInit('/cubejs/demo/worker.js', initialized)
