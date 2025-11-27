# frr
share the code/doc

好的，让我详细解释方案2中每个配置项的含义：

## 完整配置代码

```xml
<!-- 母项目 pom.xml -->
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-resources-plugin</artifactId>
                <version>3.3.1</version>
            </plugin>
        </plugins>
    </pluginManagement>
    
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-resources-plugin</artifactId>
            <executions>
                <execution>
                    <id>copy-parent-config</id>
                    <phase>process-resources</phase>
                    <goals>
                        <goal>copy-resources</goal>
                    </goals>
                    <configuration>
                        <outputDirectory>${project.build.outputDirectory}</outputDirectory>
                        <resources>
                            <resource>
                                <directory>${project.basedir}/config</directory>
                                <filtering>true</filtering>
                                <includes>
                                    <include>*.properties</include>
                                </includes>
                            </resource>
                        </resources>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

## 逐项详细解释

### 1. `<pluginManagement>` 部分
```xml
<pluginManagement>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-resources-plugin</artifactId>
            <version>3.3.1</version>
        </plugin>
    </plugins>
</pluginManagement>
```

- **`<pluginManagement>`**: 插件管理区块，定义插件的默认配置
- **作用**: 声明插件版本，让所有子项目使用统一版本，避免版本冲突
- **特点**: 这里的配置不会立即执行，只是为子项目提供模板

### 2. `<plugins>` 部分
```xml
<plugins>
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-resources-plugin</artifactId>
        <!-- 注意：这里没有version，继承自pluginManagement -->
        <executions>...</executions>
    </plugin>
</plugins>
```

- **`<plugins>`**: 实际执行插件的区块
- **作用**: 在这里配置的插件会在当前项目（母项目）和所有子项目中执行
- **特点**: 不需要指定version，自动使用pluginManagement中定义的版本

### 3. `<executions>` 执行配置
```xml
<executions>
    <execution>
        <id>copy-parent-config</id>
        <phase>process-resources</phase>
        <goals>
            <goal>copy-resources</goal>
        </goals>
        <configuration>...</configuration>
    </execution>
</executions>
```

- **`<executions>`**: 定义插件何时执行、如何执行
- **`<id>copy-parent-config</id>`**: 给这个执行任务起个唯一名称
- **`<phase>process-resources</phase>`**: 指定在Maven生命周期的哪个阶段执行
  - `process-resources` 阶段负责处理资源文件
- **`<goal>copy-resources</goal>`**: 指定执行插件的哪个目标（功能）

### 4. `<configuration>` 具体配置
```xml
<configuration>
    <outputDirectory>${project.build.outputDirectory}</outputDirectory>
    <resources>
        <resource>
            <directory>${project.basedir}/config</directory>
            <filtering>true</filtering>
            <includes>
                <include>*.properties</include>
            </includes>
        </resource>
    </resources>
</configuration>
```

- **`<outputDirectory>`**: 文件复制到哪里
  - `${project.build.outputDirectory}` = `target/classes/` (编译输出目录)
- **`<directory>`**: 从哪个目录复制文件
  - `${project.basedir}/config` = 项目根目录下的config文件夹
- **`<filtering>true</filtering>`**: 启用属性过滤，替换 `${xxx}` 占位符
- **`<includes>`**: 包含哪些文件
  - `*.properties` = 所有.properties文件

## 工作流程

1. **Maven构建启动** → 进入 `process-resources` 阶段
2. **触发插件执行** → 执行 `copy-resources` 目标
3. **读取源文件** → 从 `${project.basedir}/config` 读取 `.properties` 文件
4. **属性过滤** → 替换文件中的 `${xxx.installer.version}` 等占位符
5. **复制文件** → 将处理后的文件复制到 `target/classes/`
6. **子项目继承** → 所有子项目自动执行相同操作

## 为什么这样设计？

- **版本统一**: `pluginManagement` 确保所有项目使用相同插件版本
- **配置共享**: 母项目的 `<plugins>` 配置自动应用到所有子项目
- **灵活性**: 子项目可以在需要时覆盖特定配置
- **维护性**: 只需在母项目修改一次，所有子项目生效

这样的配置既保证了统一性，又提供了灵活性，是Maven多模块项目的最佳实践。
