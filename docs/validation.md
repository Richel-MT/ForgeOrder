[返回](./index.md)

*本文档介绍后端[core.validation](/server/core/validation/)模块。*

# 声明式数据验证
声明式数据验证框架在ForgeOrder中被广泛使用，包括但不限于：
 - 系统设置项的验证
 - 应用设置项的验证
 - 路由参数的验证

其内部实现了一个面向对象的表达式语言，用于描述验证规则。

验证器描述一个验证规则，其输入可以是单个值、多个值或运行时上下文中的值

## 示例
> 一个字符串不能为空，且长度必须在4到10之间。
```python
AllOf(
    NotEmpty(),
    Length(4, 10)
)
```

> 满足条件`A`且满足条件`B`，或者不满足条件`C`。
```python
AnyOf(
   AllOf(
        A(), B()
   ),
   Not(C())
)
```

## 验证器
验证器`Validator`用于描述验证规则，所有验证器均定义在`core.validation.validators`模块中。

### 分类

验证器从模式上讲，可分为基础验证器与组合验证器。组合验证器可以传入其他验证器，实现更复杂的验证规则。所有验证器按模式分类的示意图如下：
 - 基础验证器
    - NotEmpty
    - Interval
    - Length
    - Choices
    - FunctionHandler
 - 组合验证器
    - AnyOf
    - AllOf
    - Not
    - If
    - Elif
    - Else

基础验证器位于`core.validation.validators.basic`模块中；组合验证器位于`core.validation.validators.composite`模块中。

从功能上讲，可分为基础验证器、自定义验证器与逻辑验证器。所有验证器按功能分类的示意图如下：
 - 基础验证器
    - NotEmpty
    - Interval
    - Length
    - Choices
    - FunctionHandler
 - 自定义验证器
    - FunctionHandler
 - 逻辑验证器
    - AnyOf
    - AllOf
    - Not
    - If
    - Elif
    - Else

在接下来的文档中，将按模式分类介绍验证器。

### 类型判断
各基础验证器均有其可处理的类型，例如`Length`仅能处理`str`类型。若传入一个验证器不能处理的类型，将抛出`UnsupportedTypeError`异常。

*UnsupportedTypeError异常在core.validation.exceptions模块中定义。*

### 调用验证器与结果
调用验证器的`validate`方法，传入需要验证的值即可。该方法返回一个`ValidationResult`对象，其包含两个属性`success`，`error`。`success`属性表示验证是否成功，`error`属性表示验证失败时的错误信息。

`error`属性的类型是`ValidationError`。`ValidationError`用于验证失败时获取错误信息，而不是一个异常。

`ValidationResult`实现了`__bool__`方法，返回`success`属性的值。

### 自定义验证器
对于已有的验证器无法满足规则时，可继承`Validator`类，实现自定义验证器。

不建议使用已弃用的`FunctionHandler`，其不能实现类型的验证。


### 基础验证器

#### NotEmpty
允许传入的类型：`str`、`dict`、`list`、`None`
限制值不能空字符串、空字典、空列表或None。
错误类型：`EmptyError`

#### Interval
允许传入的类型：`int`、`float`
限制值在一个区间内。
初始化时，需传递两个参数表示最小值与最大值，传入的值可为`Boundary`对象、`int`类型或`float`类型，若传入None，则表示不限制该边界。
`Boundary`对象可以通过`Open`、`Closed`工厂函数创建。`Closed`表示闭区间（允许边界值）；`Open`表示开区间（不允许边界值）。
错误类型：`IntervalError`
示例：
```python
Interval(1, 8)                 # 表示：(1,8)
Interval(Open(1), Open(8))     # 表示：(1,8)
Interval(Open(1), Closed(8))   # 表示：(1,8]
Interval(Closed(1), Open(8))   # 表示：[1,8)
Interval(Closed(1), Closed(8)) # 表示：[1,8]
Interval(Closed(1), None)      # 表示：[1,+∞)
Interval(None, Open(1))        # 表示:(-∞,1)
Interval(Closed(1), 8)         # 表示：[1,8)
```

#### Length
允许传入的类型：`str`
限制值的长度在一个区间内。
初始化时，需传递两个参数表示最小长度与最大长度，传入的值可为`int`类型。传入的值均包含边界。
错误类型：`LengthError`

#### Choices 
允许传入的类型：`Any`
限制值必须在指定的可选值列表中。
初始化时，需传递多个参数表示可选值列表，传入的值可为任意类型。
错误类型：`ChoicesError`
示例：
```python
Choices(1, 2, 3) # 表示：限制值必须为1、2或3之一
```


#### ~~FunctionHandler~~ （已弃用）
允许传入的类型：`Any`
初始化时，需传递一个可调用对象。该对象必须允许传递一个参数，表示验证的值。返回值的类型必须为`ValidationResult`，否则将会抛出`UnsupportedVerifyHandlerError`。

*UnsupportedVerifyHandlerError异常在core.validation.exceptions模块中定义。*

### 组合验证器
组合验证器允许验证所有类型的值，但其子验证器可能有类型的限制。

#### AnyOf
传入多个验证器，值必须通过其中任意一个验证器。
错误类型：`AnyOfError`

#### AllOf
传入多个验证器，值必须通过其中所有验证器。
错误类型：`AllOfError`

#### Not
值必须不通过指定的验证器。

**`If`、`Elif`、`Else`验证器将在，`Condition`部分介绍。**


### `Condition`与`If`、`Elif`、`Else`
在处理复杂的条件时，可能希望一个值在某个条件下验证A条件，在其他条件下验证B条件。使用`If`、`Elif`、`Else`验证器和`Condition`可以实现。

`Condition`表示一个条件，其实现一个`check`方法，返回一个`bool`值。

`If`验证器是一个根据条件选择执行的验证器。使用`If`验证器时，会先判断`Condition`是否满足，若满足才进行验证。

Condition用于描述逻辑判断，不直接产生验证错误；Validator用于描述验证失败后的规则结果。

#### 内置的`Condition`
截止到目前，`Condititon`仅有一个`Equal`条件。

##### Equal
判断两个值是否相等。

#### `If`、`Elif`、`Else`的组合使用
`Elif`类继承于`If`。`Elif`与`Else`类不可单独使用，应使用`If`、`Elif`对象的`.Elif()`、`.Else()`方法使用。

示例：
```python
If(Equal(1, 2), NotEmpty())\
    Elif(Equal(3, 4), NotEmpty())\
    Else(...)
```


### `ValueProvider`
`ValueProvider`表示一个值提供器，其实现一个`get`方法。

`ValueProvider`主要用于延迟获取值，例如通过上下文获取其他值。

#### Ref
`Ref`表示从`context`中获取一个值。

初始化时提供`name`参数，表示要获取的值的名称。

`context`表示验证器的上下文，在调用验证器时传递`context`参数即可传递上下文。`context`必须实现一个`get`方法以获取值。

#### Computed
`Computed`表示调用一个函数来获取一个值。

初始化时提供`func`参数，表示要调用的函数。除此之外，还可以传递多个参数，表示函数的参数。

## 带值的验证
一般情况下，验证器只声明规则，不包含值。若遇到需要同时判断两个值的情况，例如：
> 两个变量都不为空
在这种情况下，可使用带值的验证器来实现。例如：
```python
AllOf(
   NotEmpty().bind(var_a),
   NotEmpty().bind(var_b),
)
```
`bind`方法用于验证指定来源的值，而不是调用validate时传入的值。


