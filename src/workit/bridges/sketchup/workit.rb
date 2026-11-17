# WorkitStudio for SketchUp (Ruby 2.7 and later, SketchUp 2021+).
# Copy this file into the SketchUp Plugins folder and restart SketchUp.
#
# SketchUp's Ruby has no usable background threads, so everything runs on the
# UI thread: a timer polls a non-blocking TCP server on 127.0.0.1.
require 'socket'
require 'json'
require 'stringio'
require 'securerandom'

module WorkitStudio
  PROTOCOL = 1
  BASE_PORT = 47840
  PORT_SPAN = 5
  MAX_TEXT = 200_000

  @server = nil
  @timer = nil
  @port = nil
  @polling = false

  def self.home
    ENV['WORKIT_HOME'] || File.join(Dir.home, '.workit')
  end

  def self.token
    return ENV['WORKIT_TOKEN'].strip if ENV['WORKIT_TOKEN'] && !ENV['WORKIT_TOKEN'].empty?
    path = File.join(home, 'token')
    if File.exist?(path)
      value = File.read(path).strip
      return value unless value.empty?
    end
    value = SecureRandom.hex(24)
    begin
      Dir.mkdir(home) unless Dir.exist?(home)
      File.open(path, File::WRONLY | File::CREAT | File::EXCL) { |f| f.write(value) }
    rescue StandardError
      begin
        existing = File.read(path).strip
        return existing unless existing.empty?
      rescue StandardError
        nil
      end
    end
    value
  end

  def self.jsonable(value, depth = 0)
    case value
    when nil, true, false, String, Integer then value
    when Float then value.finite? ? value : value.to_s
    when Symbol then value.to_s
    when Array then depth > 12 ? value.inspect : value.map { |v| jsonable(v, depth + 1) }
    when Hash
      depth > 12 ? value.inspect : value.each_with_object({}) { |(k, v), out| out[k.to_s] = jsonable(v, depth + 1) }
    when Geom::Point3d, Geom::Vector3d then value.to_a.map(&:to_f)
    when Length then value.to_f
    else value.inspect
    end
  end

  def self.clip(text)
    return text if text.nil? || text.length <= MAX_TEXT
    text[0, MAX_TEXT] + "\n... [truncated]"
  end

  def self.run(code, mode, label)
    model = Sketchup.active_model
    captured = StringIO.new
    old_out, old_err = $stdout, $stderr
    started = Time.now
    reply = { 'ok' => true }
    $stdout = $stderr = captured
    begin
      model.start_operation(label, true) if mode == 'modify'
      value = eval(code, TOPLEVEL_BINDING, '<workit>')
      model.commit_operation if mode == 'modify'
      reply['result'] = jsonable(value)
    rescue Exception => e # rubocop:disable Lint/RescueException
      model.abort_operation if mode == 'modify'
      reply = { 'ok' => false, 'error' => "#{e.class}: #{e.message}",
                'traceback' => clip((e.backtrace || []).first(15).join("\n")) }
    ensure
      $stdout, $stderr = old_out, old_err
    end
    reply['stdout'] = clip(captured.string)
    reply['elapsed_ms'] = ((Time.now - started) * 1000).to_i
    reply
  end

  def self.route(request)
    case request['op'] || 'ping'
    when 'ping'
      { 'ok' => true, 'result' => {
        'app' => 'sketchup', 'protocol' => PROTOCOL, 'port' => @port, 'pid' => Process.pid,
        'ruby' => RUBY_VERSION, 'version' => Sketchup.version, 'screenshot' => true,
        'file' => Sketchup.active_model.path
      } }
    when 'exec'
      return { 'ok' => false, 'error' => 'missing code' } unless request['code'].is_a?(String)
      run(request['code'], request['mode'] || 'read', request['label'] || 'WorkitStudio')
    when 'screenshot'
      width = (request['width'] || 1280).to_i
      height = (request['height'] || 800).to_i
      Sketchup.active_model.active_view.write_image(request['path'], width, height, true)
      { 'ok' => true, 'result' => { 'path' => request['path'] } }
    else
      { 'ok' => false, 'error' => "unknown op #{request['op'].inspect}" }
    end
  rescue Exception => e # rubocop:disable Lint/RescueException
    { 'ok' => false, 'error' => "#{e.class}: #{e.message}" }
  end

  def self.handle(client)
    line = nil
    line = client.gets("\n", 16 * 1024 * 1024) if IO.select([client], nil, nil, 2.0)
    return if line.nil?
    begin
      request = JSON.parse(line)
    rescue JSON::ParserError
      return # not our protocol (for example a browser): hang up silently
    end
    return unless request.is_a?(Hash)
    reply = if request['token'].to_s == token
              route(request)
            else
              { 'ok' => false, 'error' => 'bad token' }
            end
    reply['id'] = request['id'] if request.key?('id')
    client.write(JSON.generate(reply) + "\n")
  rescue StandardError => e
    puts "WorkitStudio: connection error #{e.class}: #{e.message}"
  ensure
    begin
      client.close
    rescue StandardError
      nil
    end
  end

  def self.poll
    return if @polling || @server.nil?
    @polling = true
    begin
      loop do
        client = @server.accept_nonblock(exception: false)
        break if client == :wait_readable || client.nil?
        handle(client)
      end
    rescue StandardError => e
      puts "WorkitStudio: #{e.class}: #{e.message}"
    ensure
      @polling = false
    end
  end

  def self.start
    stop
    PORT_SPAN.times do |offset|
      begin
        @server = TCPServer.new('127.0.0.1', BASE_PORT + offset)
        @port = BASE_PORT + offset
        break
      rescue SystemCallError
        @server = nil
      end
    end
    if @server.nil?
      puts "WorkitStudio: no free port from #{BASE_PORT}"
      return false
    end
    @timer = UI.start_timer(0.1, true) { poll }
    puts "WorkitStudio: sketchup is listening on 127.0.0.1:#{@port}"
    true
  end

  def self.stop
    UI.stop_timer(@timer) if @timer
    @timer = nil
    @server.close if @server
    @server = nil
  rescue StandardError
    @server = nil
  end

  unless file_loaded?(__FILE__)
    UI.menu('Extensions').add_item('WorkitStudio: restart') { start }
    file_loaded(__FILE__)
  end
  start
end
