$(function(){
	var i = 1;
	$('a.accordion-toggle').each(function(){
		$(this).attr('id', 'goal-' + i);
		++i;
	});
});

var accordionState = [];
$(function(){
	$("a.accordion-toggle").on("click", function(){
		var id = $(this).attr("id");
		var state = accordionState[id];
		if(accordionState[id] == undefined || ! accordionState[id]){
			$("a.accordion-toggle").each(function(){
				var oid = $(this).attr('id');
				accordionState[oid] = false;
				$("#" + oid + " img").css("transform", "rotate(0)");
			});
			$("#" + id + " img").css("transform", "rotate(90deg)");
			accordionState[id] = true;
		}else{
			$("#" + id + " img").css("transform", "rotate(0)");
			accordionState[id] = false;
		}
	});
});

