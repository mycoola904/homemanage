(function () {
  var ENTER_CLASS = 'billpay-row-enter';
  var LEAVE_CLASS = 'billpay-row-leave';
  var ENTER_ANIMATION_TIMEOUT_MS = 220;
  var FAST_MODE_TOGGLE_ID = 'bill-pay-fast-mode';
  var FAST_MODE_STATUS_ID = 'bill-pay-fast-mode-status';
  var pendingNextRowId = null;

  function getFastModeToggle() {
    return document.getElementById(FAST_MODE_TOGGLE_ID);
  }

  function getFastModeEnabled() {
    var toggle = getFastModeToggle();
    return !!(toggle && toggle.checked);
  }

  function getStatusElement() {
    return document.getElementById(FAST_MODE_STATUS_ID);
  }

  function clearStatusMessage() {
    var status = getStatusElement();
    if (!status) {
      return;
    }
    status.textContent = '';
    status.classList.add('hidden');
  }

  function showStatusMessage(message) {
    var status = getStatusElement();
    if (!status) {
      return;
    }
    status.textContent = message;
    status.classList.remove('hidden');
  }

  function syncFastModeField(container) {
    if (!(container instanceof HTMLElement)) {
      return;
    }
    var value = getFastModeEnabled() ? '1' : '0';
    Array.from(container.querySelectorAll('[data-fast-mode-field]')).forEach(function (input) {
      if (input instanceof HTMLInputElement) {
        input.value = value;
      }
    });
  }

  function clearEnterTimer(row) {
    if (!isBillPayRow(row)) {
      return;
    }

    var timerId = row.getAttribute('data-billpay-enter-timeout-id');
    if (timerId) {
      clearTimeout(Number(timerId));
      row.removeAttribute('data-billpay-enter-timeout-id');
    }
  }

  function isBillPayRow(element) {
    return element instanceof HTMLElement &&
      (element.hasAttribute('data-billpay-animate-row') || (element.id && element.id.indexOf('bill-pay-row-') === 0));
  }

  function restartEnterAnimation(row) {
    if (!isBillPayRow(row)) {
      return;
    }

    clearEnterTimer(row);
    row.classList.remove(ENTER_CLASS);
    row.classList.remove(LEAVE_CLASS);
    row.offsetWidth;

    row.classList.add(ENTER_CLASS);
    var timeoutId = setTimeout(function () {
      clearEnterAnimation(row);
    }, ENTER_ANIMATION_TIMEOUT_MS);
    row.setAttribute('data-billpay-enter-timeout-id', String(timeoutId));
  }

  function clearEnterAnimation(row) {
    if (!isBillPayRow(row)) {
      return;
    }
    clearEnterTimer(row);
    row.classList.remove(ENTER_CLASS);
  }

  function maybeApplyLeaveAnimation(row) {
    if (!isBillPayRow(row)) {
      return;
    }

    if (row.getAttribute('data-billpay-enable-leave') === 'true') {
      row.classList.add(LEAVE_CLASS);
    }
  }

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
    if (!(detailTarget instanceof HTMLElement)) {
      return;
    }

    if (isBillPayRow(detailTarget)) {
      restartEnterAnimation(detailTarget);
    }

    var row = detailTarget.closest('[data-billpay-edit-row]');
    if (row instanceof HTMLElement) {
      syncFastModeField(row);
      focusInitial(row);
      if (pendingNextRowId && row.getAttribute('data-account-id') === pendingNextRowId) {
        pendingNextRowId = null;
        clearStatusMessage();
      }
    }
  });

  document.body.addEventListener('htmx:configRequest', function (event) {
    var target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    var row = target.closest('[data-billpay-edit-row]');
    if (!(row instanceof HTMLElement)) {
      return;
    }
    if (!event.detail || !event.detail.parameters) {
      return;
    }
    event.detail.parameters.fast_mode = getFastModeEnabled() ? '1' : '0';
    syncFastModeField(row);
  });

  document.body.addEventListener('htmx:responseError', function (event) {
    var detailTarget = event.detail && event.detail.target;
    if (!(detailTarget instanceof HTMLElement)) {
      return;
    }
    if (pendingNextRowId && detailTarget.id === 'bill-pay-row-' + pendingNextRowId) {
      pendingNextRowId = null;
      showStatusMessage('Unable to open the next row. Continue manually.');
    }
  });

  document.body.addEventListener('billpay:openNextRow', function (event) {
    var payload = event.detail || {};
    var nextRowId = payload.nextRowId;
    var nextEditUrl = payload.nextEditUrl;
    if (!nextRowId || !nextEditUrl) {
      return;
    }

    var targetRow = document.getElementById('bill-pay-row-' + nextRowId);
    if (!(targetRow instanceof HTMLElement)) {
      showStatusMessage('Unable to open the next row. Continue manually.');
      return;
    }

    pendingNextRowId = String(nextRowId);
    clearStatusMessage();
    if (window.htmx && typeof window.htmx.ajax === 'function') {
      window.htmx.ajax('GET', nextEditUrl, {
        target: targetRow,
        swap: 'outerHTML'
      });
      return;
    }

    showStatusMessage('Unable to open the next row. Continue manually.');
  });

  document.body.addEventListener('htmx:beforeSwap', function (event) {
    var detailTarget = event.detail && event.detail.target;
    if (!(detailTarget instanceof HTMLElement)) {
      return;
    }

    if (isBillPayRow(detailTarget)) {
      maybeApplyLeaveAnimation(detailTarget);
    }
  });

  document.body.addEventListener('animationend', function (event) {
    var target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    if (event.animationName !== 'billpay-row-enter') {
      return;
    }

    clearEnterAnimation(target);
  });

  document.addEventListener('DOMContentLoaded', function () {
    var row = activeEditRow();
    if (row) {
      syncFastModeField(row);
      focusInitial(row);
    }
    clearStatusMessage();
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
