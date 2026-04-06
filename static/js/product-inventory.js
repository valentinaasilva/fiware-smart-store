(function () {
  function parseAvailableShelves(row) {
    if (!row) {
      return [];
    }

    try {
      const parsed = JSON.parse(row.dataset.availableShelves || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (_error) {
      return [];
    }
  }

  function fillShelfSelect(selectNode, shelves, placeholderLabel) {
    if (!selectNode) {
      return;
    }

    selectNode.innerHTML = "";

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = placeholderLabel;
    selectNode.appendChild(placeholder);

    shelves.forEach(function (shelf) {
      const option = document.createElement("option");
      option.value = shelf.id;
      option.textContent = shelf.name || shelf.shortId || shelf.id;
      selectNode.appendChild(option);
    });
  }

  function toggleStoreForm(button, formRow) {
    if (!button || !formRow) {
      return;
    }

    const isHidden = formRow.classList.contains("is-hidden");
    formRow.classList.toggle("is-hidden", !isHidden);
    button.setAttribute("aria-expanded", isHidden ? "true" : "false");

    if (!isHidden) {
      return;
    }

    const shelves = parseAvailableShelves(formRow);
    const selectNode = formRow.querySelector(".js-shelf-target-select");
    const submitButton = formRow.querySelector("button[type='submit']");
    const emptyMsgNode = formRow.querySelector(".js-no-shelf-msg");

    fillShelfSelect(selectNode, shelves, selectNode?.dataset.placeholder || "Select shelf");

    const hasOptions = shelves.length > 0;
    if (selectNode) {
      selectNode.disabled = !hasOptions;
    }
    if (submitButton) {
      submitButton.disabled = !hasOptions;
    }
    if (emptyMsgNode) {
      emptyMsgNode.classList.toggle("is-hidden", hasOptions);
    }
  }

  function initProductStoreForms() {
    const buttons = document.querySelectorAll(".js-toggle-product-store-form");
    if (buttons.length === 0) {
      return;
    }

    buttons.forEach(function (button) {
      const targetId = button.dataset.targetForm;
      if (!targetId) {
        return;
      }

      const row = document.getElementById(targetId);
      if (!row) {
        return;
      }

      const selectNode = row.querySelector(".js-shelf-target-select");
      if (selectNode && !selectNode.dataset.placeholder) {
        const firstOption = selectNode.querySelector("option");
        selectNode.dataset.placeholder = firstOption ? firstOption.textContent : "Select shelf";
      }

      button.setAttribute("aria-expanded", "false");
      button.addEventListener("click", function () {
        toggleStoreForm(button, row);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProductStoreForms);
  } else {
    initProductStoreForms();
  }
})();
