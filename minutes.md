Finn Crawford (z5309129) 
Benjamin Short (z5362873) 
Harry Le (z5363583) 
Shourya Saklecha (z5392153) 
Jason Solanki (z5360354) 


Template 

Author: 

When: 

Attendees: 

Absentees: N/A 

Agenda 

Discussion 

Actionable 

Who? 

When? 

What work has been assigned? 




Week 2 

Author: Shourya Saklecha 

When: Sunday 4:30pm 27/2 

Attendees: Benjamin, Jason, Finn, Shourya 

Absentees: Harry Le 

Agenda 

Discussion:

    Figuring out a data structure 

    We discussed our potential options for the data structures we can use. We concluded that dictionaries are the best possible option for us.  

Order of Functions: 

    Clear_v0, Authorizations, Channel creations, details, channel join, channel invites,  

 

Actionable 

Who? 

When? 

Clear_v1, auth_login_v1, auth_register_v1 (Benjamin Short): Monday 

Channels_create_v1, channel_details_v1 (Finn Crawford): Wednesday 

Channels_list_v1, channel_listall_v1 (Harry Le):Friday (Before Lab) 

Channel_join_v1, channel_invite_v1 (Jason Solanki): Friday (Before Lab) 

Channel_messages_v1 (Shourya Saklecha): Saturday 


For Next Week: Standup on Tuesday night; Meeting on Saturday.  

 

Week 3 

Author: Finn 

When: 9:15 1/3/22 

Attendees: Benjamin, Jason, Finn, Shourya, Harry  

Absentees: N/A 

Agenda 

Discussion:

    Stand up - Ben 

        Finished auth_register_v1 and auth_login_v1 

        Some trouble with handle 

        Explained data structure 

    Stand up - Finn 

        Nearly done channels_create_v1 and channel_details_v1 

        Some trouble with key values in channel_details_v1 

        Fix tonight 

        Fixing bugs 

        Fixed bugs in channel_details_v1 (calling pop unnecessarily, made new dict instead) 

 

Actionable 

Who? 

When? 

Merge channel_details_v1, channels_create_v1 (Finn): Tonight 

Channels_list_v1, channel_listall_v1 (Harry Le): Saturday 

Channel_join_v1, channel_invite_v1 (Jason Solanki): Friday (Before Lab) 

Channel_messages_v1 (Shourya Saklecha): Saturday 

 

Week 3 Weekend 

Author: Finn 

When: 5pm 

Attendees: Harry, Ben, Shourya, Jason 

Absentees: N/A 

Agenda 

Discussion:

    Stand up- Shourya 

        Finished messages function that’s passing tests 

        Discussed what we need to for iter1 (not much) 

    Stand up - Harry 

        Talked about how we can use channel_details_v1 to get all the details like if 
        auth_user_id is in all_members and ispublic 

        Had trouble because of hand 

 

Actionable 

Who? 

When? 

Finish channels list functions and tests (Harry): 10:30pm tonight 

 

Week 4 Lab 

Author: Jason 

When: 11/03/2022 - 2pm 

Attendees: Benjamin, Jason, Finn, Shourya, Harry 

Absentees: N/A 

Agenda 

Discussion:

    Iteration 2 Start 

    Pick the order of implementing the functions 

    Assigning functions to each member 

    Regular Meeting Time: 10am Mondays (Weekly – All Members) 

 

Actionable 

Who? 

When? 

Benjamin:

    auth/login/v2, auth/register/v2: 
        13/03/2022 
    auth/logout/v1, admin/userpermission/change/v1:
        16/03/2022
    admin/user/remove/v1:
        TBD

Jason: 

    channel/join/v2, channel/invite/v2:
        13/03/2022
    channel/addowner/v1, channel/leave/v1, channel/removeowner/v1:
        16/03/2022 

Finn: 

    channels/create/v2, channel/details/v2, users/all/v1:
        13/03/2022
    user/profile/setemail/v1, user/profile/sethandle/v1, user/profile/setname/v1:
        16/03/2022
    dm/create/v1, dm/details/v1, dm/leave/v1:
        TBD 

Shourya:

    channel/messages/v2:
        13/03/2022
    message/send/v1, message/edit/v1:
        16/03/2022
    dm/messages/v1, message/senddm/v1, message/remove/v1:
        TBD 

Harry:

    channels/list/v2, channels/listall/v2:
        13/03/2022
    dm/list/v1, user/profile/v1, dm/remove/v1:
        TBD

MEETING:
    Date: March 16, 2022, 8:30 PM
    Author: Shourya
    Attendees: Finn, Benjamin, Harry, Shourya, Jason
    Agenda: Checkup, Troubleshooting, Planning
    Absentees: None

Updates:


Benjamin:
    Completed auth_register, auth_login.
    Still working on tokens and auth_logout
    Clear_v2() completed

Finn:
    Catching up on classes, working on channel_create and channel_details.
    Completing functions by Friday Lab.

Shourya:
    Reviewed the channel_messages_v1 error.
    Catch up on lectures, complete 'dm' functions by Sunday evening.

Harry:
    Reviewed lectures
    Will finish functions on the weekend.

Jason:
    Did the meeting minutes and merged it into the repository.
    Working on functions over the weekend.
    Reviewed merge requests.

Discussion:
    Next Deadline: Monday, 21st March: Three function rows from the dependencies
    Next meeting Scheduled: 21st March, Monday
    Re-assigning a few functions between Finn Jason and Ben




STANDUP: 
Date: 21st March 2022
Author: Shourya 
Attendees: Benjamin, Finn, Shourya
Absentees: Jason, Harry

Updates: 

Benjamin: 
    1. Completed tokens. 
    2. Validated errors. 
    3. Will complete auth_logout and permissions.

Finn: 
    1. Completed channels create and details. 
    2. Completed wrappers.
    3. Created the route file
    4. Completed all the user functions and tests. 

Shourya: 
    1. Reviewed Finn's code, merged into master. 
    2. Wrote tests for channel/messagesv2

Discussion: 
    1. Re scheduling deadlines.
    2. Coverage
    3. Getting fixtures into src
    4. Next Meeting: Thursday 1 pm. 



