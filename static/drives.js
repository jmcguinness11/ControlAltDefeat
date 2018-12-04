// This file controls the drives page

$(window).bind('load', function() {
    var table = document.getElementById('drives')

    //source - https://stackoverflow.com/questions/17120633/loop-through-each-html-table-column-and-get-the-data-using-jquery
    $(table).find('tr').each(function(i, el) {
        var $tds = $(this).find('td') 
        var series = $tds.get(0)
        var gain = $tds.get(5)
        if(gain) {
            input = $(gain).find('input').get(0)
            value = parseInt($(input).attr('value'))
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
                scaled_val = Math.floor(-255*(-5-value)/5)
                color = "rgb(255," + scaled_val + "," + scaled_val + ")"
                all_inputs = $($tds).find('input').each(function() {
                    in_list = $(this).get(0)
                    $(in_list).css("background-color", color)
                })
                $($tds).css("background-color", color)
            } else {
                series_val = 1;
                series_input = $(series).find('input').get(0)
                if(series) {
                    series_val = parseInt($(series_input).attr('value'))
                }
		color = "rgb(205, 201, 201)"
                
                //set color to white if it's a break between series
                if(isNaN(series_val)) {
                    color = "rgb(255, 255, 255)"
                } else {
                    $(gain).text("No gain")
                    console.log($(gain).text())
                }
                all_inputs = $($tds).find('input').each(function() {
                    in_list = $(this).get(0)
                    $(in_list).css("background-color", color)
                })
                $($tds).css("background-color", color)
	    }
        }
    })
})
