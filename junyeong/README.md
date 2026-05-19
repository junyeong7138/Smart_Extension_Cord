
>>> %Run main.py
SPI 포트가 안전하게 닫혔습니다.
Traceback (most recent call last):
  File "/home/wattsup/Project/junyeong/RaspberryPi/main.py", line 42, in <module>
    main()
  File "/home/wattsup/Project/junyeong/RaspberryPi/main.py", line 28, in main
    dashboard = AIDashboardUI(dsp_engine=engine)
  File "/home/wattsup/Project/junyeong/RaspberryPi/NILM/ai_extension.py", line 460, in __init__
    super().__init__(*args, **kwargs)
  File "/home/wattsup/Project/junyeong/RaspberryPi/dashboard_ui.py", line 9, in __init__
    self.buffer_size = self.engine.buffer_size
AttributeError: 'AIEngine' object has no attribute 'buffer_size'
>>> 