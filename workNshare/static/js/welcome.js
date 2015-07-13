jQuery(document).ready(function() {

	//for showing login portion of site on click
	jQuery('button[id="login_button"]').click(function(){
		jQuery('#loginview').css('display','inline');
		var loginorsignup_top_position = $('#loginview').offset().top;
		$('html, body').animate({scrollTop:loginorsignup_top_position}, 'slow');

	});

	//for back-to-top button
    var offset = 90;
    var duration = 100;
    jQuery(window).scroll(function() {
        if (jQuery(this).scrollTop() > offset) {
            jQuery('.back-to-top').fadeIn(duration);
        } else {
            jQuery('.back-to-top').fadeOut(duration);
        }
    });

    jQuery('.back-to-top').click(function(event) {
        event.preventDefault();
        jQuery('html, body').animate({scrollTop: 0}, duration);
        return false;
    });



})
jQuery(document).ready(function() {

	    jQuery('#searched_user').typeahead({
	    	items:12,
	    	  source: function (query, process) {
	    		    return jQuery.get('/guess_users/', { query: query }, function (data) {
	    		      return process(data.options);
	    		    });
	    		  },
	    		  minLength:2,
	    		  autoSelect:false,

	    highlighter: function (item) {
	        var regex = new RegExp( '(' + this.query + ')', 'gi' );
	        return item.replace( regex, "<strong style='color:green;'>$1</strong>" );
	    },
	    });


	    })

	    jQuery(document).ready(function() {

		    jQuery('#share_username').typeahead({
		    	items:12,
		    	  source: function (query, process) {
		    		    return jQuery.get('/guess_friends/', { query: query }, function (data) {
		    		      return process(data.options);
		    		    });
		    		  },
		    		  minLength:2,
		    		  autoSelect:false,

		    highlighter: function (item) {
		        var regex = new RegExp( '(' + this.query + ')', 'gi' );
		        return item.replace( regex, "<strong style='color:red;' >$1</strong>" );
		    },
		    });
	    })



