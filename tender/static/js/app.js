"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

jQuery.extend(jQuery.validator.messages, {
  required: "Это поле необходимо заполнить.",
  remote: "Пожалуйста, введите правильное значение.",
  email: "Пожалуйста, введите корретный адрес электронной почты.",
  url: "Пожалуйста, введите корректный URL.",
  date: "Пожалуйста, введите корректную дату.",
  dateISO: "Пожалуйста, введите корректную дату в формате ISO.",
  number: "Пожалуйста, введите число.",
  digits: "Пожалуйста, вводите только цифры.",
  creditcard: "Пожалуйста, введите правильный номер кредитной карты.",
  equalTo: "Пароли не совпадают",
  accept: "Пожалуйста, выберите файл с правильным расширением.",
  maxlength: jQuery.validator.format("Пожалуйста, введите не больше {0} символов."),
  minlength: jQuery.validator.format("Пожалуйста, введите не меньше {0} символов."),
  rangelength: jQuery.validator.format("Пожалуйста, введите значение длиной от {0} до {1} символов."),
  range: jQuery.validator.format("Пожалуйста, введите число от {0} до {1}."),
  max: jQuery.validator.format("Пожалуйста, введите число, меньшее или равное {0}."),
  min: jQuery.validator.format("Пожалуйста, введите число, большее или равное {0}."),
  extension: jQuery.validator.format("Вы можете загрузить изображение только со следующими расширениями: jpeg, jpg, png, gif.")
});

function formSubmit(form, callbacks) {
  var response_cont = $(form).find('.js-response-text'),
      options = {
    beforeSubmit: function beforeSubmit() {
      response_cont.hide();
      $(form).find('[type="submit"]').addClass('loading').attr('disabled', 'disabled');
    },
    success: function success(data) {
      if (data.status && data.redirectURL && data.redirectURL != '') {
        window.location.href = data.redirectURL;
      }
      if (data.status && data.confirmEmail) {
        $('.complete_registration').click();
      }
      $(form).find('[type="submit"]').removeClass('loading').removeAttr('disabled');
      if (callbacks && callbacks.success) {
        callbacks.success(data);
      }
      if (data.responseText) {
        response_cont.show().html(data.responseText);
      }
    },
    error: function error(data) {
      response_cont.show().text('Server error, try again later.');
      $(form).find('[type="submit"]').removeClass('loading').removeAttr('disabled');
    }
  };
  $(form).ajaxSubmit(options);
}

var Forms = function Forms() {
  _classCallCheck(this, Forms);

  $('#form-signin').validate({
    rules: {
      email: {
        required: true,
        email: true
      },
      password: {
        required: true
      }
    },
    submitHandler: function submitHandler(form) {
      formSubmit(form, {});
      return false;
    }
  });
  $('#form-signup').validate({
    rules: {
      email: {
        required: true,
        email: true
      },
      password: {
        required: true
      },
      password_verify: {
        required: true,
        equalTo: "#reg-password"
      }
    },
    submitHandler: function submitHandler(form) {
      formSubmit(form, {});
      return false;
    }
  });
};

var Overlay = function () {
  function Overlay(_overlay, _open, _popup) {
    _classCallCheck(this, Overlay);

    var t = this;
    this.$overlay = $(_overlay);
    this._open = _open;
    this._popup = _popup;
    this.timeout = false;
    $(document).on('click', '[' + t._open + ']', function (e) {
      t.show($(this).attr(t._open));
      e.stopPropagation();
      e.preventDefault();
    });
    $('[' + t._popup + ']').on('click', function (e) {
      if (!$(e.target).is('[' + t._open + ']')) {
        e.stopPropagation();
      }
    });
    $(document).on('click', function () {
      t.hide();
    });
  }

  _createClass(Overlay, [{
    key: "show",
    value: function show(popupName) {
      var t = this;
      var $popup = $('[' + t._popup + '="' + popupName + '"]');
      if (t.$overlay.hasClass('active')) {
        t.hide(true);
        $popup.addClass('active');
      } else {
        setTimeout(function () {
          t.$overlay.add($popup).addClass('active');
        }, 10);
      }
      t.$overlay.add($popup).show().removeClass('faded');
      clearTimeout(t.timeout);
    }
  }, {
    key: "hide",
    value: function hide(change) {
      var t = this;
      var $popup = $('[' + t._popup + '].active');
      if (change) {
        $popup.hide();
      } else {
        t.$overlay.removeClass('active').addClass('faded');
      }
      $popup.removeClass('active').addClass('faded');
      t.timeout = setTimeout(function () {
        t.$overlay.add($popup).hide().removeClass('faded');
      }, 500);
    }
  }]);

  return Overlay;
}();

$(function () {
  new Overlay('.js-overlay', 'data-open-popup', 'data-popup-name');
  new Forms();
});
//# sourceMappingURL=app.js.map
