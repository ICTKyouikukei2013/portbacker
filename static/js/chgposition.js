$(function() {
  $(window).scroll(function () {
    // if there are tags to have input_diary class (used in porsonallog.html)
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

    // if there are tag to have input_diary class (used in goal.html)
    var grapharea = $('.graph-area'),
        offset = grapharea.offset();

    if($(window).scrollTop() > 130) {
        grapharea.css('position', 'fixed');
        grapharea.css('left', offset.left);
    } else {
        grapharea.css('position', 'relative');
        grapharea.css('left', '');
    }
  });
});
