SET SERVEROUTPUT ON
select * from FND_PROFILE_OPTION_VALUES where rownum = 1;
DBMS_OUTPUT.PUT_LINE('success');
/
EXIT;