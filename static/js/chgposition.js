$(window).scroll(function () {
	var input_diary = $('.input_diary');
	var width = input_diary.css('width');

	if($(window).scrollTop() > 130) {
   		input_diary.css('position', 'fixed');
    	input_diary.css('top', '30px');
    	input_diary.css('width', width);
 	} else {
    	input_diary.css('position', 'relative');
    	input_diary.css('top', '0px');
    	input_diary.css('width', '');
  	}
});
