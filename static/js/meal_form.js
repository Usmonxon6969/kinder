document.addEventListener("DOMContentLoaded", () => {
  // Add ingredient button click handler
  const addIngredientBtn = document.getElementById("add-ingredient")
  const ingredientFormset = document.getElementById("ingredient-formset")

  if (addIngredientBtn && ingredientFormset) {
    addIngredientBtn.addEventListener("click", () => {
      const forms = document.querySelectorAll(".ingredient-form")
      const formNum = forms.length
      const totalForms = document.getElementById("id_ingredients-TOTAL_FORMS")

      // Clone the last form
      const newForm = forms[forms.length - 1].cloneNode(true)

      // Update form index
      const newFormIndex = formNum
      newForm.innerHTML = newForm.innerHTML.replace(/ingredients-\d+/g, `ingredients-${newFormIndex}`)

      // Clear input values
      const inputs = newForm.querySelectorAll("input, select")
      inputs.forEach((input) => {
        if (input.type !== "hidden" || !input.name.includes("id")) {
          input.value = ""
        }
      })

      // Fix IDs and labels on newly added form
      const labels = newForm.querySelectorAll("label")
      labels.forEach((label) => {
        const forAttr = label.getAttribute("for")
        if (forAttr) {
          label.setAttribute("for", forAttr.replace(/\d+/, newFormIndex))
        }
      })

      // Add new form to the DOM
      ingredientFormset.appendChild(newForm)

      // Update total forms count
      totalForms.value = formNum + 1

      // Setup delete button for the new row
      setupDeleteButton(newForm.querySelector(".delete-row"))
    })
  }

  // Setup delete buttons for existing ingredients
  function setupDeleteButton(button) {
    button.addEventListener("click", function () {
      const formRow = this.closest(".ingredient-form")
      const deleteCheckbox = formRow.querySelector('input[type="checkbox"][name$="-DELETE"]')

      if (deleteCheckbox) {
        deleteCheckbox.checked = true
        formRow.style.display = "none"
      } else {
        // For new forms that don't have a DELETE checkbox
        formRow.remove()
      }
    })
  }

  // Initialize delete buttons for existing rows
  const deleteButtons = document.querySelectorAll(".delete-row")
  deleteButtons.forEach(setupDeleteButton)
})
