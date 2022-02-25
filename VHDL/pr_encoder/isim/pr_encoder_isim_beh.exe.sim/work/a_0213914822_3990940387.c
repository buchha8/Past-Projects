/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                       */
/*  \   \        Copyright (c) 2003-2009 Xilinx, Inc.                */
/*  /   /          All Right Reserved.                                 */
/* /---/   /\                                                         */
/* \   \  /  \                                                      */
/*  \___\/\___\                                                    */
/***********************************************************************/

/* This file is designed for use with ISim build 0xc4ca3437 */

#define XSI_HIDE_SYMBOL_SPEC true
#include "xsi.h"
#include <memory.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
static const char *ng0 = "C:/Users/buchha2/Desktop/code/VHDL/pr_encoder/pr_encoder.vhd";



static void work_a_0213914822_3990940387_p_0(char *t0)
{
    char *t1;
    char *t2;
    unsigned char t3;
    unsigned char t4;
    int64 t5;
    char *t7;
    char *t8;
    char *t9;
    char *t10;
    char *t11;
    char *t12;
    char *t13;
    char *t14;
    unsigned char t15;
    unsigned char t16;
    int64 t17;
    char *t19;
    char *t20;
    char *t21;
    char *t22;
    char *t23;
    char *t24;
    char *t25;
    char *t26;
    unsigned char t27;
    unsigned char t28;
    int64 t29;
    char *t31;
    char *t32;
    char *t33;
    char *t34;
    char *t35;
    char *t36;
    char *t37;
    char *t38;
    unsigned char t39;
    unsigned char t40;
    int64 t41;
    char *t43;
    char *t44;
    char *t45;
    char *t46;
    char *t47;
    char *t48;
    int64 t49;
    char *t50;
    char *t52;
    char *t53;
    char *t54;
    char *t55;
    char *t56;
    char *t57;
    char *t58;

LAB0:    xsi_set_current_line(29, ng0);
    t1 = (t0 + 1032U);
    t2 = *((char **)t1);
    t3 = *((unsigned char *)t2);
    t4 = (t3 == (unsigned char)3);
    if (t4 != 0)
        goto LAB3;

LAB4:    t13 = (t0 + 1192U);
    t14 = *((char **)t13);
    t15 = *((unsigned char *)t14);
    t16 = (t15 == (unsigned char)3);
    if (t16 != 0)
        goto LAB5;

LAB6:    t25 = (t0 + 1352U);
    t26 = *((char **)t25);
    t27 = *((unsigned char *)t26);
    t28 = (t27 == (unsigned char)3);
    if (t28 != 0)
        goto LAB7;

LAB8:    t37 = (t0 + 1512U);
    t38 = *((char **)t37);
    t39 = *((unsigned char *)t38);
    t40 = (t39 == (unsigned char)3);
    if (t40 != 0)
        goto LAB9;

LAB10:
LAB11:    t49 = (5 * 1000LL);
    t50 = (t0 + 5028);
    t52 = (t0 + 3232);
    t53 = (t52 + 56U);
    t54 = *((char **)t53);
    t55 = (t54 + 56U);
    t56 = *((char **)t55);
    memcpy(t56, t50, 2U);
    xsi_driver_first_trans_delta(t52, 0U, 2U, t49);
    t57 = (t0 + 3232);
    xsi_driver_intertial_reject(t57, t49, t49);

LAB2:    t58 = (t0 + 3152);
    *((int *)t58) = 1;

LAB1:    return;
LAB3:    t5 = (5 * 1000LL);
    t1 = (t0 + 5020);
    t7 = (t0 + 3232);
    t8 = (t7 + 56U);
    t9 = *((char **)t8);
    t10 = (t9 + 56U);
    t11 = *((char **)t10);
    memcpy(t11, t1, 2U);
    xsi_driver_first_trans_delta(t7, 0U, 2U, t5);
    t12 = (t0 + 3232);
    xsi_driver_intertial_reject(t12, t5, t5);
    goto LAB2;

LAB5:    t17 = (5 * 1000LL);
    t13 = (t0 + 5022);
    t19 = (t0 + 3232);
    t20 = (t19 + 56U);
    t21 = *((char **)t20);
    t22 = (t21 + 56U);
    t23 = *((char **)t22);
    memcpy(t23, t13, 2U);
    xsi_driver_first_trans_delta(t19, 0U, 2U, t17);
    t24 = (t0 + 3232);
    xsi_driver_intertial_reject(t24, t17, t17);
    goto LAB2;

LAB7:    t29 = (5 * 1000LL);
    t25 = (t0 + 5024);
    t31 = (t0 + 3232);
    t32 = (t31 + 56U);
    t33 = *((char **)t32);
    t34 = (t33 + 56U);
    t35 = *((char **)t34);
    memcpy(t35, t25, 2U);
    xsi_driver_first_trans_delta(t31, 0U, 2U, t29);
    t36 = (t0 + 3232);
    xsi_driver_intertial_reject(t36, t29, t29);
    goto LAB2;

LAB9:    t41 = (5 * 1000LL);
    t37 = (t0 + 5026);
    t43 = (t0 + 3232);
    t44 = (t43 + 56U);
    t45 = *((char **)t44);
    t46 = (t45 + 56U);
    t47 = *((char **)t46);
    memcpy(t47, t37, 2U);
    xsi_driver_first_trans_delta(t43, 0U, 2U, t41);
    t48 = (t0 + 3232);
    xsi_driver_intertial_reject(t48, t41, t41);
    goto LAB2;

LAB12:    goto LAB2;

}


extern void work_a_0213914822_3990940387_init()
{
	static char *pe[] = {(void *)work_a_0213914822_3990940387_p_0};
	xsi_register_didat("work_a_0213914822_3990940387", "isim/pr_encoder_isim_beh.exe.sim/work/a_0213914822_3990940387.didat");
	xsi_register_executes(pe);
}
