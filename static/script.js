function showCheckboxes(id) {
    var checkboxes = document.getElementById(id);
    if (checkboxes != null) {
      var expanded = checkboxes.style.display === "block";
      if (!expanded) {
        checkboxes.style.display = "block";
      } else {
        checkboxes.style.display = "none";
      }
    }
  }
  // Bind the checkboxes together
  $(document).on('click', 'input[type="checkbox"]', function() {
    var $this = $(this);
    var id = $this.attr('id');
    var isChecked = $this.prop('checked');
    $('input[type="checkbox"][name="' + $this.attr('name') + '"]').each(function() {
        $(this).prop('checked', isChecked);
    });
  });



