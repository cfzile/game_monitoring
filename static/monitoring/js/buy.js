$(".add_in_basket").on("click", function(event){

    const pos = $(this).attr("id").substr(4);
    const min_date = new Date();
    const from_date_datepicker = $('#' + pos + '_from').datepicker('getDate');
    const to_date_datepicker = $('#' + pos + '_to').datepicker('getDate');

    const getDateAsStr = function(date){
        const f = function (str) {
            while (str.toString().length < 2)
                str = '0' + str;
            return str;
        };
        return f(date.getMonth() + 1) + "/" + f(date.getDate()) + "/" + date.getFullYear();
    };

    if (from_date_datepicker !== null && to_date_datepicker != null && from_date_datepicker <= to_date_datepicker) {

        var from_date = new Date(from_date_datepicker.getFullYear(), from_date_datepicker.getMonth(), from_date_datepicker.getDate());
        var to_date = new Date(to_date_datepicker.getFullYear(), to_date_datepicker.getMonth(), to_date_datepicker.getDate());
        var period = new Date(to_date - from_date)/1000/60/60/24 + 1;
        var name_pos = $("#name_pos_" + pos).text();
        var price = $("#price_" + pos).text();

        var current_date = new Date(from_date);
        var busy_days_num = 0;
        var disabled_dates = $('#' + pos + '_from').datepicker("option", "disabledDates");

        while (current_date <= to_date) {
            var date = jQuery.datepicker.formatDate('mm/dd/yy', current_date); // TODO
            if (jQuery.inArray(date, disabled_dates) !== -1 || current_date.getDate() < min_date.getDate())
                ++busy_days_num;
            current_date.setDate(current_date.getDate() + 1);
        }

        period -= busy_days_num;

        if ($(this)[0].checked){
            $("#check_list").append("<tr class=\"basket_" + pos + "\">" +
                "<td>" + name_pos + "</td><td>от " + getDateAsStr(from_date) + " до " + getDateAsStr(to_date) + " " + period +" дней</td><td><span id=\"basket_price_" + pos + "\">" + (price * period) + "</span> руб.</tdbasket_></tr>");
            $("#total_check").text(parseFloat($("#total_check").text()) + (price * period));
            $(".pay_block form").append("<input type=\"hidden\" id=\"check_pos_" + pos + "\" name=\"pos_" + pos + "\" value=\"" + pos + "\">");
            $(".pay_block form").append("<input type=\"hidden\" id=\"check_period_" + pos + "\" name=\"period_" + pos + "\" value=\"" + period + "\">");
            $(".pay_block form").append("<input type=\"hidden\" id=\"check_data_from_" + pos + "\" name=\"data_from_" + pos + "\" value=\"" + getDateAsStr(from_date) + "\">");
            $(".pay_block form").append("<input type=\"hidden\" id=\"check_data_to_" + pos + "\" name=\"data_to_" + pos + "\" value=\"" + getDateAsStr(to_date) + "\">");
        }else{
            $("#total_check").text(parseFloat($("#total_check").text()) - $("#basket_price_" + pos).text());
            $("#check_pos_" + pos).remove();
            $("#check_period_" + pos).remove();
            $("#check_data_from_" + pos).remove();
            $("#check_data_to_" + pos).remove();
            $(".basket_" + pos).remove();
        }

    }else{
        $(this).prop("checked", false);
        alert("Выбирите даты");
    }

});