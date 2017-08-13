/*	code: prevent scrolling inside of block */

	function noScroll(className) {
		$( '.'+className ).bind( 'mousewheel DOMMouseScroll', function ( e ) {
			var e0 = e.originalEvent,
				delta = e0.wheelDelta || -e0.detail;
			this.scrollTop += ( delta < 0 ? 1 : -1 ) * 30;
			e.preventDefault();
		});
	}
/*	code: end */

/*	code: select text with one click */
	function selectText(containerid) {
		if (document.selection) {
			var range = document.body.createTextRange();
			range.moveToElementText(document.getElementById(containerid));
			range.select();
		} else if (window.getSelection) {
			var range = document.createRange();
			range.selectNode(document.getElementById(containerid));
			window.getSelection().addRange(range);
		}
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
	$.fancybox('/ajax/seminar_simple/'+seminar_id+'/', {
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


function showAskLektor(seminar_id)
{
	$.fancybox('/ajax/ask_lektor/'+seminar_id+'/', {
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
