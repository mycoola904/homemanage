(function () {
  function orderedControls(row) {
    return Array.from(row.querySelectorAll('[data-tab-order]'))
      .sort(function (left, right) {
        return Number(left.getAttribute('data-tab-order')) - Number(right.getAttribute('data-tab-order'));
      });
  }

  function focusByField(row, field) {
    if (!row) {
      return;
    }
    var selector = '[data-focus-field="' + field + '"]';
    var target = row.querySelector(selector);
    if (!target) {
      var controls = orderedControls(row);
      target = controls.length ? controls[0] : null;
    }
    if (target) {
      target.focus();
    }
  }

  function focusInitial(row) {
    var initial = row.getAttribute('data-initial-focus-field') || 'actual_payment_amount';
    focusByField(row, initial);
  }

  function activeEditRow() {
    return document.querySelector('[data-billpay-edit-row]');
  }

  document.body.addEventListener('htmx:afterSwap', function (event) {
    var detailTarget = event.detail && event.detail.target;
    var row = detailTarget instanceof HTMLElement ? detailTarget.closest('[data-billpay-edit-row]') : null;
    if (!(row instanceof HTMLElement)) {
      return;
    }
    focusInitial(row);
  });

  document.addEventListener('DOMContentLoaded', function () {
    var row = activeEditRow();
    if (row) {
      focusInitial(row);
    }
  });

  document.body.addEventListener('keydown', function (event) {
    var target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    var row = target.closest('[data-billpay-edit-row]');
    if (!(row instanceof HTMLElement)) {
      return;
    }

    var controls = orderedControls(row);
    if (!controls.length) {
      return;
    }

    if (event.key === 'Tab') {
      var currentIndex = controls.indexOf(target);
      if (currentIndex === -1) {
        return;
      }
      event.preventDefault();
      var direction = event.shiftKey ? -1 : 1;
      var nextIndex = (currentIndex + direction + controls.length) % controls.length;
      controls[nextIndex].focus();
      return;
    }

    if (event.key === 'Enter') {
      if (target.tagName === 'TEXTAREA') {
        return;
      }
      event.preventDefault();
      var saveButton = row.querySelector('[data-focus-field="save"]');
      if (saveButton instanceof HTMLElement) {
        saveButton.click();
      }
      return;
    }

    if (event.key === 'Escape') {
      event.preventDefault();
      var cancelButton = row.querySelector('[data-focus-field="cancel"]');
      if (cancelButton instanceof HTMLElement) {
        cancelButton.click();
      }
    }
  });
})();
