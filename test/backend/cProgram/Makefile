all:
	$(MAKE) -f Makefile.maintest all
	$(MAKE) -f Makefile.test001 all
	$(MAKE) -f Makefile.test2 all
	$(MAKE) -f Makefile.test3 all

maintestBuild:
	$(MAKE) -f Makefile.maintest all

test001Build:
	$(MAKE) -f Makefile.test001 all

test2Build:
	$(MAKE) -f Makefile.test2 all

test3Build:
	$(MAKE) -f Makefile.test3 all


maintestRun:
	$(MAKE) -f Makefile.maintest run

test001Run:
	$(MAKE) -f Makefile.test001 run

test2Run:
	$(MAKE) -f Makefile.test2 run

test3Run:
	$(MAKE) -f Makefile.test3 run

clean:
	$(MAKE) -f Makefile.maintest clean
	$(MAKE) -f Makefile.test001 clean
	$(MAKE) -f Makefile.test2 clean
	$(MAKE) -f Makefile.test3 clean

fclean:
	$(MAKE) -f Makefile.maintest fclean
	$(MAKE) -f Makefile.test001 fclean
	$(MAKE) -f Makefile.test2 fclean
	$(MAKE) -f Makefile.test3 fclean

re: fclean all

.PHONY: all maintestBuild maintestRun test001Build test001Run test2Build test2Run test3Build test3Run clean fclean re
