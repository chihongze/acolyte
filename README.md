# Acolyte

## 概述

Acolyte是一个软件发布、部署的串联工具，传统CI工具的工作流程多是专注于监听版本控制 => 创建环境 => 获取最新的代码副本 => 执行构建 => 运行测试用例 => 反馈结果。然而在复杂的工程实践中，这些事情只是其中的一个环节，真实的发布部署流程中往往会存在繁琐复杂的人机交互，甚至是需要跨部门的参与，比如SQL审核、代码review、QA对测试结果的反馈、灰度发布及回滚等等，我们需要有一个工具将这些流程串联起来，并对相关人员进行引导，同时能记录和展示每一次的工作进度、历史以及收集每个环节的数据。Acolyte就是一个这样的工具，它提供了一个流程框架，允许你根据自己的开发流程快速构建出一个串联系统。

## 基本元素

Acolyte本质上是一个交互式的工作流，用户通过编写一个FlowMeta类来定义一个工作流，工作流的每个环节通过一个Job来表示。

### Job

Job描述了Flow中一个环节的处理逻辑，一个Job是由一个或多个Action组成的，比如在我们的开发流程中，项目经过TravisCI构建成功后，接下来会被让运维部署到沙箱环境当中，部署到沙箱的这个过程就可以被抽象为一个SandboxJob：

```python
from acolyte.core.job import (
	AbstractJob,
	JobArg
)
from acolyte.util.validate import (
	StrField,
)

class SandboxJob(AbstractJob):

	def __init__(self):
		super().__init__(
			name="sandbox",
			description="部署jar包到沙箱",
			job_args={
				"trigger": [
					JobArg("version", StrField("version", required=True), mark=JobArg.MARK_AUTO, comment="Jar包版本号")
				],
				"reject": [
					JobArg("reason", StrField("reason", required=True, min_len=10), mark=JobArg.MARK_AUTO, comment="拒绝原因")
				]
			}
		)
		
	def on_trigger(self, context, version):
		ops_email = get_ops_email()
		send_mail(
			receiver=ops_email,
			subject="运维哥哥求部署到沙箱, 版本: {}".format(version),
			mail_content=render_mail(version=version)
		)
		
	def on_agree(self, context):
		deploy_to_sandbox()
		send_mail(
			receiver=get_dev_email(),
			subject="成功部署到沙箱！",
			mail_content=render_mail()
		)
		context.finish()  # 标记该Job已经被完成了
		
	def on_reject(self, context, reason):
		send_mail(
			receiver=get_dev_email(),
			subject="目前无法部署到沙箱",
			mail_content=render_mail(reason=reason)
		)
		context.save(data={"reason": reason})
		context.stop()  # 无法部署到沙箱，此次部署行动失败，flow终止
```

每个Job都需要去继承AbstractJob，并且包含一些on_xxx方法，每个这样的方法就是一个action，其中on\_trigger方法是必须要定义的，它描述了该Job被触发时所进行的动作，在这个例子中，SandboxJob被触发时会给运维发送一封邮件，告诉运维jar包已经就绪，可以部署到沙箱了。运维收到邮件之后，可以选择两个动作，点击同意部署，就会触发on\_agree方法，将jar包部署到沙箱，通过调用context.finish()来标记该Job已经成功结束；如果不同意，那么会触发on\_disagree方法，并且传递一个reason参数来告诉开发当前因为某某原因无法部署到沙箱，通过调用context.stop()方法会标记整个flow终止，无法继续前进下去。

每个on\_xxx方法都可以接受一个上下文对象和一些自定义的参数，上下文对象(context)可以提供数据存储以及一些操控flow运行流程的方法：

```
# 可以像字典一样存取数据，这样保存的数据在flow的执行期内有效，可用于Job之间的数据传递
context["a"] = "hehe"
print(context["a"])

# 将当前Action的计算数据保存起来，这些数据可以用于在web平台上渲染Job终端页
# 比如测试成败、测试覆盖率之类的数据都可以这样保存
context.save({"reason": reason})

# context.finish() # 标记当前Job可以成功结束，Flow可以安全运行下个Job
# context.stop() # 该Job失败，Flow无法继续前进，用该方法标记终止
```

每个action其余所需要的自定义参数会通过在构造方法中由bind\_args进行声明，每个JobArg代表一个参数声明，其中包含了该参数的名称、验证规则、mark以及注释。

<b>定义参数验证规则</b>

为确保传递给action的参数是正确无误的，Acolyte要求您必须声明每个参数的验证规则，您只需要声明规则即可，Acolyte会根据这些规则自动为您把关每一次用户输入。

规则通过acolyte.util.validate.Field对象来进行声明：

```
Field(
	name: ...,
	type_: ...,
	required: ...,
	default: ...,
	value_of: ...,
	check_logic: ...
)
```

* name: 参数名称
* type_: 期望的类型，比如int或者str等等
* required: 该字段是不是必须的
* default: 如果不是必须的，请提供一个默认值
* value\_of: 如果该字段不能满足期望的类型，那么可以通过该函数来对值进行转换，比如通过int()将一个字符串转换从整形，如果该函数依旧转型失败，那么就会返回类型错误了。
* check\_logic: 用户自定义的校验逻辑

同时Field类派生了IntField和StrField这两个子类：

```
IntField(
	name: ...,
	required: ...,
	default: ...,
	value_of: ...,
	min_: ..., 
	max_: ...,
	check_logic: ...
)
```

* min\_: 该参数不能小于min\_所指定的值。
* max\_: 该参数不能大于max\_所指定的值。

```
StrField(
	name: ..., 
	required: ...,
	default: ..., 
	value_of: ...,
	min_len: ..., 
	max_len: ...,
	regex: ...,
	check_logic: ...
)
```

* min\_len: 该参数长度不能低于min\_len所指定的值
* max\_len: 该参数长度不能大于max\_len所指定的值
* regex: 该参数必须满足此正则表达式


<b>mark</b>

mark参数描述了参数值的覆盖规则。

* JobArg.MARK\_AUTO: auto参数，用户的输入可以覆盖flow meta和flow template中的绑定默认值。
* JobArg.MARK\_STATIC: static参数，该参数的最终值只能由flow template和flow meta来定义，flow template可以覆盖flow meta中绑定的值，但是用户的输入是无法覆盖此值的。
* JobArg.MARK\_CONST: const参数，只能由flow meta来绑定，其余层级无法覆盖此值。

关于flow meta和flow template的概念会在flow的描述中说明。

<b>comment</b>

描述该参数的作用，会在帮助页面中展示。

所有的Job都会通过JobManager进行管理，通过name进行引用，JobManager通过acolyte.job_definition这个entry\_point来在应用初始化时加载并实例化所有的Job，基于entry\_point加载的优势在于您可以随意在您自己的项目中定义Job，acolyte都能找到并加载它们。

### Flow

Flow是Job的组合，但是它拥有三个层次的形态：

* FlowMeta: 最原始的Flow定义，由Job按顺序编排而成。
* FlowTemplate: 由对FlowMeta一些参数的覆盖而得来，比如虽然公司完成了对部署流程的统一，大家都可以使用同一个FlowMeta定义的流程，但是各个部门之间有一些默认参数是存在差异的，那么每个部门就可以基于同一个FlowMeta配置各自的FlowTemplate。
* FlowInstance: 当一个FlowTemplate运行起来的时候，描述此次运行的过程就是FlowInstance对象。

嗯，可以把FlowMeta理解成一个函数，FlowTemplate理解成一个FlowMeta被Currying之后的函数，FlowInstance是该函数的一次具体执行过程。

#### Flow Meta

定义一个FlowMeta：

```python
class TestFlowMeta(FlowMeta):

    def __init__(self):
        super().__init__(
            name="test_flow",
            description="just a test flow",
            jobs=(
                JobRef(
                    step_name="pull_request",
                    job_name="pull_request",
                    trigger={
							
                    },
                ),
                JobRef(
                		step_name="code_review",
                		job_name="code_review",
                ),
                JobRef(
                		step_name="sandbox",
                		job_name="sandbox"
                ),
                ...
          ))
          
    def on_start(self, ctx, argA, argB, ...):
    	# do something init
    	...
    	
    def on_stop(self, ctx):
    	...
    	
    def on_finish(self, ctx):
    	...
```

定义FlowMeta必须继承一个FlowMeta基类，并在构造方法中传递一串Job定义，通过JobRef来引用一个Job，可以在一个FlowMeta中引用多次相同的Job，但必须通过step_name将它们区分开。通过JobRef还可以为每个Job的Action指定默认的参数值。

FlowMeta还提供了三个生命周期方法，即on\_start，on\_stop、on\_finish:

1. on\_start: 在FlowInstance刚刚创建完成之后运行，此时还没有任何Job被执行。
2. on\_stop: 当有Job中的context.stop()被执行时会触发该方法，即Flow被人为终止。
3. on\_finish：当所有flow中的所有Job都被执行完毕之后会回调该方法。

FlowMeta需要硬编码在项目中，系统会通过一个FlowMetaManager来管理所有的FlowMeta对象，同Job一样，也是基于entry\_point的管理方式：acolyte.flow\_meta\_definition。

#### Flow Template

Flow Template是基于FlowMeta创建，创建FlowTemplate无需写代码，直接调用接口即可，例如

```
[PUT] /v1/flow/template

req body:

{
	flow_meta_name: "deploy",
	template_name: "deploy_for_rest",
	bind_args: {
		pull_request: {
			trigger: {
				...
			}
		}
	},
	max_run_instance: 1,
	description: "REST项目组专用部署流程"
}
```

* flow\_meta\_name: 基于的flow meta名称
* template\_name: 新建template的名称
* bind\_args: 绑定参数，不能绑定被mark为const的参数，层次为step\_name=>action\_name=>args
* max\_run\_instance: 最大同时运行实例数目，比如我在同一时间只允许一个REST项目的部署流程在跑，那么就可以指定为1，Acolyte会在FlowInstance启动时进行检查，确保同一时间只有指定数目的实例运行。
* description: 说明


#### Flow Instance

<b>启动一个实例</b>

当某一事件触发时（比如通过Github webhook检测到有人pull requests），调用该接口来创建一个Flow Instance

```
[POST] /v1/flow/template/{flow_template_id}/start

req_body

{
	initiator: 100010,
	description: "庆十五大更新！",
	start_flow_args: {
		...
	}
}
```

* initiator: 触发用户ID
* description: 此次任务描述
* start\_flow\_args: 触发FlowMeta中on\_start事件的参数

<b>执行某个Job</b>


```
[POST] /v1/flow/instance/{flow_instance_id}/{step_name}/{action}

# 如果是trigger，则{action}可省略

req_body

{
	actor: 100010,
	action_args: {
		...
	}
}
```

* actor: 执行人ID
* action\_args: 执行指定动作所需要的参数，比如TravisCI构建完毕之后，您可以在after\_success中将构建好的包上传到文件存储，然后调用该接口 [POST] /v1/flow/instance/{flow\_instance\_id}/sandbox接口，并将构建包的路径通过action\_args传递给trigger，这样运维就可以在通知中通过该路径获取已经构建好的包。如果运维同意构建，则会调用[POST] /v1/flow/instance/{flow\_instance\_id}/sandbox/agree接口，不同意则会调用[POST] /v1/flow/instance/{flow\_instance\_id}/sandbox/disagree接口。

该接口是执行FlowInstane的主力接口，虽然是主动发起的，但是在执行时会执行严格的参数校验以及流程校验，只有当flow中定义的该step之前的所有job都运行无误后才可以运行。

### REST API

除了上述控制流程的API，还有各种获取执行状态和数据的API，还未整理完全。

### Job的实现

如果没有Job，那么Acolyte就是一个空壳，什么都干不了，如果有丰富的Job类型，那么Acolyte可以从CI、CD甚至是处理离职申请环节无所不能。会先针对CI先写一些通用的内置Job：Github Webhook处理的相关Job、TravisCI构建结果处理的Job，然后开发公司专用的CI组件包，比如Sandbox部署、灰度发布，这些在每个公司是不一样的。

### 自定义UI

设想每个Job可以为自己定义UI页面，也就说Acolyte会为Job产生的数据提供存取接口，具体的前端展示会由Job来自己定义，具体怎么抽象还没想好，做到这里再说吧。

### 用户与权限

最开始只有一个token系统，细致的权限控制流程跑通后再加。