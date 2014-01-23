var commentCount = 0;

$(function() {
	$('#popup').on("click", function(){
		var range = window.getSelection().getRangeAt(0);
		var selectionContents = range.extractContents();
		var span = document.createElement("span");
		commentCount += 1;
		span.id = "popupid" + commentCount;
		span.style.background = "yellow";
		span.appendChild(selectionContents);
		range.insertNode(span);

		comment = $('textarea').val();
		$('#' + span.id).balloon({ contents: comment });
	});
});
