$(document).ready(function(){
	// this config is loaded when using mobile device on page `/feedback/`
	// using fancybox on mobiles instead of highslide gallery

	// remove `onclick` event which triggers highslide
	$('.feedback-img').prop('onclick',null).off('click');

	// init fancybox instead
	$('.feedback-img').fancybox();
});