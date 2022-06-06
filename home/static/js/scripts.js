
 

jQuery(document).ready(function($) {
    $(".clickable_name").click(function() {
        window.location = $(this).data("href");
    });
});


$(document).ready(function () {
    $('#dtBasicExample').DataTable();
    $('.dataTables_length').addClass('bs-select');
});

$(document).ready(function () {
    $('#mycustomnav li a').click(function(e) {
        $('#mycustomnav li.active').removeClass('active');

        var $parent = $(this).parent().parent();

        $parent.addClass('active');
        e.preventDefault();
        window.location.href = e.target.href

    });
});
