��    b      ,  �   <      H      I  '   j     �     �     �     �     �     �     �     �     �     �  	   �     		  
   	  
   !	     ,	     >	     U	     m	     �	     �	     �	     �	     �	  
   �	  	   �	     
     
  +   
  /   B
  @   r
  U   �
  Y   	  Y   c  :   �     �     
  
        %  	   ;     E     V     f     v     |  
   �     �     �     �     �     �  z   �     3     6     C     Q  3   ]     �     �  
   �     �     �  J   �     "  5   ;  9   q  D   �  (   �          9     W  $   o  &   �     �     �     �  
   �     �  k     '   o  9   �     �     �     �       +        :     I  
   W     b     p     �     �     �     �  	   �  D  �  !     *   1     \     i     p     }     �     �     �     �     �     �     �     �  	   �     �     �               '     7     M     f     s     �     �  	   �  	   �     �     �  !   �     �  $     0   1  E   b     �  	   �     �     �     �     �               "     5     <     I     V     ]     p     w     ~     �     �     �     �     �     �     �     �     �     �     �            *   -     X     n     {  	   �  	   �     �     �     �     �     �     �     �     �  $   
     /     E     X     h     o  	   v     �     �     �     �     �     �     �     �  	   �     �     �     >   @   
   V   %   &   /          J   O   P           R       ^   =   -              T   C   F                                     X           #      (   *      Q   M   N   W         I      .       Y          ]                     1   6      H   :   7       E      K          !       `       B   <   S      D   ,      L   G               5   a         4       2   '   Z       	      8   $              ;   _      A   U   3              \       ?       +   b   )          "   0   9       [    A node is basic unit of Workflow A transfer is from a node to other node Action Args Active Add View Allow to reset the Workflow And Apply Auto Cancel Cancel WorkFollow Setting Code Condition Create event Created by Created on Custom WorkFollow Custom WorkFollow Node Custom WorkFollow Trans Custom WorkFollow Transfer Default  States to display Default Workflow State value Display Name Event Users Field Workflow-State Force note From Node Group Reset Groups If True, This Workflow allow to reset draft If True, This node will show in Workflow states If True, this Node not display the Reset button, default is True If true, When Workflow arrived this node, will create a calendar event relation users If true, the Workflow note can not be empty, usually when transfer is Reverse,you need it If true, when condition is True,transfer will auto finish, not need button, default false If you want record something for this transfer, write here Incoming Transfer Invisible Reset Is Reverse Is a Reverse transfer Join Mode Last Modified on Last Updated by Last Updated on Model Model  View Model Name Name No Reset States Node Nodes Note OR:anyone input Transfers approved, will arrived this node.  AND:must all input Transfers approved, will arrived this node Or Out Transfer Python Action Resource ID Select a model that you want to create the Workflow Sequence Show In Workflow Split Mode TO Node The Workflow State field The auto created Workflow extend view, show Workflow button, state, logs.. The calendar event users The check condition of this transfer, default is True The default Workflow state, It is come from the star node The form view of the model that want to extend Workflow button on it The groups who can process this transfer The input transfer of this node The out transfer of this node The transfer had finish This node is the end of the Workflow This node is the start of the Workflow Transfer Transfer Log Transfer log Transfers, Update WorkFollow Setting When arrived this node, you can set to trigger a object function to do something, example confirm the order Which state u can to reset the Workflow Which status can show the state widget, It is set by node WorkFollow Logs WorkFollow Node WorkFollow Transfer Workflow Workflow Reset Button Groups, default Admin Workflow Start Workflow Stop XML Groups log.wkf.trans the object function args wizard.wkf.message wk.wizard.message wkf.base wkf.node wkf.trans Project-Id-Version: Odoo Server 12.0
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2019-06-27 11:51+0000
PO-Revision-Date: 2019-06-27 20:13+0800
Last-Translator: <>
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
Language: zh_CN
X-Generator: Poedit 2.2.3
 节点是基本的工作流单位 迁移是从一个节点到另一个节点 动作参数 有效 添加视图 允许重置工作流 和 应用 自动 取消 撤销工作流设置 代码 条件 创建事件 创建人 创建时间 自定义工作流 工作流节点 工作流迁移 工作流迁移 默认显示的状态 默认工作流状态值 显示名称 事件的的用户 状态字段 必须备注 源节点 重置组 群组 允许重置工作流 节点显示在工作流状态中 节点显示重置按钮 创建日历事件的工作流节点 必须备注才能审核，一般用于反审核 自动迁移，设置为真，迁移会自动完成，默认为假。 为迁移添加备注 源迁移 隐藏重置按钮 是反向的 反向迁移 加入模式 最后修改日 最后更新者 最后更新时间 模型 模型视图 模型名称 名称 不可重置状态 节点 节点 备注 或 或 迁出 代码动作 资源ID 工作流模型 序号 显示工作流 拆分模式 去向节点 工作流状态字段 工作流的扩展视图 日历事件用户 迁移条件计算表达式，默认为真 默认工作流状态 模型视图 迁移按钮权限 入迁移 出迁移 完成的迁移 结束节点 开始节点 调拨 迁移日志 迁移日志 迁移 更新工作流设置 到达这个节点，触发的动作 可以重置的状态 显示的状态点 工作流日志 节点 迁移 工作流 重置权限组 开始 停止 XML组 工作流日志 参数 消息 消息 工作流 节点 迁移 