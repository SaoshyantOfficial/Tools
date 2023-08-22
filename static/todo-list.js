// todo-list.js
document.addEventListener("DOMContentLoaded", function () {
    const dailyButton = document.getElementById("daily-button");
    const weeklyButton = document.getElementById("weekly-button");
    const dailyTable = document.getElementById("daily-table");
    const weeklyTable = document.getElementById("weekly-table");
    const dailyActivity = document.getElementById('daily_activity');
    const weeklyActivity = document.getElementById('weekly_activity');
    const daily_Button = document.getElementById('daily_button');
    const weekly_Button = document.getElementById('weekly_button');



    dailyButton.addEventListener("click", function () {
        weeklyActivity.style.display = 'none'
        weekly_Button.style.display = 'none'
        dailyActivity.style.display = 'block'
        daily_Button.style.display = 'block'
        dailyTable.style.display = "table";
        weeklyTable.style.display = "none";
        dailyButton.classList.add("active");
        weeklyButton.classList.remove("active");
    });

    weeklyButton.addEventListener("click", function () {
        dailyActivity.style.display = 'none'
        daily_Button.style.display = 'none'
        weeklyActivity.style.display = 'block'
        weekly_Button.style.display = 'block'
        weeklyTable.style.display = "table";
        dailyTable.style.display = "none";
        weeklyButton.classList.add("active");
        dailyButton.classList.remove("active");
    });
});
