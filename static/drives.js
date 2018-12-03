// This file controls the drives page

$(window).bind('load', function() {
    var table = document.getElementById('drives')

    //source - https://stackoverflow.com/questions/17120633/loop-through-each-html-table-column-and-get-the-data-using-jquery
    $(table).find('tr').each(function(i, el) {
        var $tds = $(this).find('td') 
        var gain = $tds.get(4)
        if(gain) {
            input = $(gain).find('input').get(0)
            value = parseInt($(input).attr('value'))
	    console.log(value)
            if(value > 0) {
                value = Math.min(value,10)
                scaled_val = Math.floor(255*(10-value)/10)
                color = "rgb(" + scaled_val + ",255," + scaled_val + ")"
                all_inputs = $($tds).find('input').each(function() {
                    in_list = $(this).get(0)
                    $(in_list).css("background-color", color)
                })
                $($tds).css("background-color", color)
            } else if(value < 0) {
                value = Math.max(value,-5)
                scaled_val = Math.floor(255*(-5-value)/5)
                color = "rgb(255," + scaled_val + "," + scaled_val + ")"
                all_inputs = $($tds).find('input').each(function() {
                    in_list = $(this).get(0)
                    $(in_list).css("background-color", color)
                })
                $($tds).css("background-color", color)
            } else {
		console.log("here")
		color = "rgb(205, 201, 201)"
                all_inputs = $($tds).find('input').each(function() {
                    in_list = $(this).get(0)
                    $(in_list).css("background-color", color)
                })
                $($tds).css("background-color", color)
	    }
        }
        //console.log($tds.html())
    })
})
