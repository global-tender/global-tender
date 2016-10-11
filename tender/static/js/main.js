/*	code: prevent scrolling inside of block */
	$(document).ready(function (){
		noScroll('subscribe_region_list');
	});

	function noScroll(className) {
		$( '.'+className ).bind( 'mousewheel DOMMouseScroll', function ( e ) {
			var e0 = e.originalEvent,
				delta = e0.wheelDelta || -e0.detail;
			this.scrollTop += ( delta < 0 ? 1 : -1 ) * 30;
			e.preventDefault();
		});
	}
/*	code: end */


$(document).ready(function() {

	$('.main-info-text').hover(function(){
		$('.down-link').animate({"bottom":"-2%"}, 'slow');
	}, function(){
		$('.down-link').animate({"bottom":"-2%"}, 'slow');
	});

	$('.main-info-text').hover(function(){
		$('.down-link').animate({"bottom":"2%"}, 'slow');
	}, function() {
		$('.down-link').animate({"bottom":"2%"}, 'slow');
	});


	if ($('.sem-phone'))
	{
		$('.sem-phone').mask('+0 (000) 000-00-00');
	}


	$('.subscr_popup_hide').on('click', function(){
		$('.subscr_popup').animate({'left':'-620'},400)
	});

	$('.main-info-text').hover(function(){
		if ($('.subscr_popup').css('left') == '-620px')
		{
			$('.subscr_popup').animate({'left':'0'},400)
		}
	});

});

var down_link = (function(){
	$(document).on('click', '.down-link', function(){
		$('html, body').animate({
			scrollTop: $(window).height()
		});
		return false;
	});
})();


function showSeminarForm(seminar_id)
{
	$.fancybox('/ajax/seminar/'+seminar_id+'/', {
		type:'ajax',

		autoSize: true,
		fitToView: false,
		maxWidth: "100%",

		modal: true,
		helpers: {
			overlay:{
				locked:true,
				closeClick: false,
			}
		},
	});

	return false;
}

function showAskQuestion()
{
	$.fancybox('/ajax/question/',{type:'ajax',helpers:{overlay:{locked:true}}});
	return false;
}


function ajaxFormTry(ajaxForm){

	if ($('input[name="submit_message"]').length)
		$('input[name="submit_message"]').val('Ожидайте...');

	if ($('.seminar-submit-button').length)
		$('.seminar-submit-button').text('Ожидайте...');

	$.post(
		ajaxForm.attr('action'),
		ajaxForm.serialize(),
		function(data){
			$.fancybox.open(data);
	});
	return false;
}


$(document).ready(function() {

	var subscribe_region_border_bottom = $('.subscribe_region').css('border-bottom');
	var subscribe_region_border_radius = $('.subscribe_region').css('border-radius');

	$('.subscribe_region').on('click', function(){
		if ($('.subscribe_region_list').css('height') == '0px') {

			$('.subscribe_region').css('border-bottom', '0px');
			$('.subscribe_region').css('border-bottom-left-radius', '0px');
			$('.subscribe_region').css('border-bottom-right-radius', '0px');

			$('.subscribe_region_list').animate({ height: '150' }, 'slow');
			$('.subscribe_region_button').css('background-position', '10px -183px');

		}
		else {

			$('.subscribe_region_list').animate(
				{ height: '0' },
				'slow',
				function(){
					$('.subscribe_region').css('border-bottom', subscribe_region_border_bottom);
					$('.subscribe_region').css('border-radius', subscribe_region_border_radius);
				});
			$('.subscribe_region_button').css('background-position', '10px -117px');

		}
	});
});