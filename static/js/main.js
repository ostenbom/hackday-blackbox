function navigateIFrame(link) {
  document.getElementById('concourse-iframe').src = link;
}

function fullscreenConcourse() {
  document.getElementById('concourse-box').style.width = '100%'
  document.getElementById('blackbox-box').style.visibility = 'hidden'
}

function halfscreenConcourse() {
  document.getElementById('concourse-box').style.width = '50%'
  document.getElementById('blackbox-box').style.visibility = 'visible'
}

document.onkeyup = function(e) {
  console.log('kepup')
  if (e.altKey && e.which == 70) {
    fullscreenConcourse()
  } else if (e.altKey && e.which == 72) {
    halfscreenConcourse()
  }
};
