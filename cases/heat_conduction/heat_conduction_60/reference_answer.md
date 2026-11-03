# 问题34解析参考

该初值是单一本征模态：

```text
T(x,y,t)=300+100*sin(pi*x)*sin(4*pi*y)
               *exp{-0.01*[pi^2+(4*pi)^2]*t}.
```

标准答案：`python3 analytic_reference.py --case 34`
