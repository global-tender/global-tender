
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

});

var down_link = (function(){
	$(document).on('click', '.down-link', function(){
		$('html, body').animate({
			scrollTop: $(window).height()
		});
		return false;
	});
})();

var Popup = (function(){

	allow = true;
	opened = false;
	var show = function(popup) {
		if(!allow) return;
		$('.overlay').addClass('active').css('z-index', 99);
		$('.pop-window[data-popup=' + popup + ']').removeClass('closed');
		$('html').css('overflow', 'hidden');
		opened = popup;
	}

	var close = function(popup) {
		allow = false;
		$('.overlay').removeClass('active');
		$('html').removeAttr('style');
		setTimeout(function(){
			$('.overlay').css('z-index', -1);
			$('.pop-window[data-popup=' + popup + ']').addClass('closed');
			allow = true;
			opened = false;
		}, 500);
	}

	$(document).on('click', '.js-pop-close', function(){
		if(opened) {
			close(opened);
		}
		return false;
	});

	$(document).on('click', '.js-pop-show', function(){
		if(!opened) {
			show($(this).attr('data-popup'));
		}
		return false;
	});

	if(window.location.hash != '') {
		show(window.location.hash.substr(1));
	}

	return { show: show, close: close };
})();



