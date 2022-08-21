

// console.log('script present');

let options = ['Major/Year', 'Random']

for(let i = 0; i < options.length; i++)
{
    let opt = options[i];
    let btn = document.getElementById("toggle-button-" + opt);
    // console.log('try setup for ', opt);
    btn.addEventListener('click', function()
    {
        // console.log('make ', opt, 'active')
        if(btn.classList.contains('inactive-button'))
        {
            btn.classList.remove('inactive-button');
            for(let j = 0; j < options.length; j++)
            {
                let otherOpt = options[j];

                if(otherOpt != opt)
                {
                    document.getElementById("toggle-button-" + otherOpt).classList.remove('active-button');
                    document.getElementById("toggle-button-" + otherOpt).classList.add('inactive-button');
                    // console.log('remove active for ', opt);
                }
            }
            btn.classList.add('active-button');
        }
        
    });
}
